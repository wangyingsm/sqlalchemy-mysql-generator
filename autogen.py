#!/bin/env python
# -*- coding: utf8 -*-

import pymysql as pm

def check_and_connect(args):
    if 'host' not in args or not args['host']:
        raise AttributeError()
    if 'user' not in args or not args['user']:
        raise AttributeError()
    if 'database' not in args or not args['database']:
        raise AttributeError()
    if 'password' not in args or not args['password']:
        conn = pm.connect(host=args['host'], user=args['user'], database=args['database'], charset='utf8')
    else:
        conn = pm.connect(host=args['host'], user=args['user'], 
        password=args['password'], database=args['database'], charset='utf8')
    return conn

def get_all_tables(conn):
    cursor = conn.cursor()
    cursor.execute('show tables')
    tables = cursor.fetchall()
    cursor.close()
    return tables

def get_all_columns(conn, tablename):
    cursor = conn.cursor()
    cursor.execute('desc %s' %tablename)
    columns = cursor.fetchall()
    cursor.close()
    return columns

def parse_columns(columns, camel_case):
    fields = []
    for col in columns:
        line = col[1].split('(')
        if len(line)>1:
            type = line[0]
            size = line[1][:-1]
        else:
            type = line[0].lower()
            size = 0
        if col[2].lower() == 'no':
            nullstr = ', nullable=False'
        else:
            nullstr = ''
        if col[3].lower() == 'pri':
            prikeystr = ', primary_key=True'
        else:
            prikeystr = ''
        if col[4]:
            defaultstr = ', default=%s' %col[4]
        else:
            defaultstr = ''
        if camel_case:
            fieldname = camelCaseFieldName(col[0])
        else:
            fieldname = col[0]
        if type in ('bit', 'bool'):
            fieldstr = '%s = db.Column("%s", db.Boolean%s%s%s)' %(fieldname, col[0], prikeystr, nullstr, defaultstr)
            fields.append(fieldstr)
            continue
        if type in ('tinyint', 'smallint', 'mediumint', 'int', 'integer', 'bigint'):
            fieldstr = '%s = db.Column("%s", db.Integer%s%s%s)' %(fieldname, col[0], prikeystr, nullstr, defaultstr)
            fields.append(fieldstr)
            continue
        if type in ('float', 'double'):
            fieldstr = '%s = db.Column("%s", db.Float%s%s%s)' %(fieldname, col[0], prikeystr, nullstr, defaultstr)
            fields.append(fieldstr)
            continue
        if type in ('char', 'varchar'):
            if defaultstr:
                dps = defaultstr.split('=')
                defaultstr = dps[0] + "='" + dps[1] + "'"
            fieldstr = '%s = db.Column("%s", db.String(%s)%s%s%s)' %(fieldname, col[0], size, prikeystr, nullstr, defaultstr)
            fields.append(fieldstr)
            continue
        if type in ('date'):
            fieldstr = '%s = db.Column("%s", db.Date%s%s%s)' %(fieldname, col[0], prikeystr, nullstr, defaultstr)
            fields.append(fieldstr)
            continue
        if type in ('time'):
            fieldstr = '%s = db.Column("%s", db.Time%s%s%s)' %(fieldname, col[0], prikeystr, nullstr, defaultstr)
            fields.append(fieldstr)
            continue
        if type in ('datetime', 'timestamp'):
            fieldstr = '%s = db.Column("%s", db.DateTime%s%s%s)' %(fieldname, col[0], prikeystr, nullstr, defaultstr)
            fields.append(fieldstr)
            continue
        if type in ('tinytext', 'text', 'mediumtext', 'longtext'):
            if defaultstr:
                dps = defaultstr.split('=')
                defaultstr = dps[0] + "='" + dps[1] + "'"
            fieldstr = '%s = db.Column("%s", db.Text%s%s%s)' %(fieldname, col[0], prikeystr, nullstr, defaultstr)
            fields.append(fieldstr)
            continue
        if type in ('tinyblob', 'blob', 'mediumblob', 'longblob', 'binary', 'varbinary'):
            fieldstr = '%s = db.Column("%s", db.LargeBinary%s%s%s)' %(fieldname, col[0], prikeystr, nullstr, defaultstr)
            fields.append(fieldstr+'\n')
            continue
    return fields

def camelCaseClassName(s):
    return ''.join(map(lambda x: x.capitalize(), s.split('_')))

def camelCaseFieldName(s):
    fields = s.split('_')
    return fields[0] + ''.join(map(lambda x: x.capitalize(), fields[1:]))

def write_entities(conn, tables, conf):

    for tb in tables:
        tn = tb[0]
        if conf['tables'] and tn not in conf['tables']:
            continue
        if conf['exclude'] and tn in conf['exclude']:
            continue
        tn_ = tn
        if conf['tableNamePrefix']:
            for p in conf['tableNamePrefix']:
                if tn.startswith(p):
                    tn_ = tn[len(p):]
        if conf['toCamelCase']:
            tn_ = camelCaseClassName(tn_)
        import os
        if not os.path.exists(conf['output']):
            os.mkdir(conf['output'])
        with open(conf['output']+'/'+tn_+'.py', 'w') as fn:
            fn.write('''# -*- coding: utf8 -*-

from sqlalchemy_serializer import SerializerMixin as mixin
''')
            fn.write('from %s import %s\n\n\n' %(conf['dbModule'], conf['dbVariable']))
            fn.write('class %s(db.Model, mixin):\n' %tn_)
            fn.write(' '*4 + '__tablename__ = "%s"\n\n' %tn)
            fields = parse_columns(get_all_columns(conn, tn),  conf['toCamelCase'])
            for f in fields:
                fn.write(' '*4+f+'\n')
            fn.write('\n')

def parse_config(configfile):
    import chardet
    with open(configfile, 'rb') as fn:
        data = fn.read()
        lines = data.decode(chardet.detect(data)['encoding'])
    import json
    conf = json.JSONDecoder().decode(lines)
    return conf

if __name__=='__main__':
    import sys
    if len(sys.argv) < 2:
        print('Usage: python autogen.py [CONFIG JSON FILE]')
        exit(-1)
    conf = parse_config(sys.argv[1])
    conf['host'] = conf['host'] if 'host' in conf else 'localhost'
    conf['user'] = conf['user'] if 'user' in conf else 'root'
    conf['password'] = conf['password'] if 'password' in conf else ''
    conf['database'] = conf['database'] if 'database' in conf else 'test'
    conf['output'] = conf['output'] if 'output' in conf else 'out_entities'
    conf['dbModule'] = conf['dbModule'] if 'dbModule' in conf else 'app'
    conf['dbVariable'] = conf['dbVariable'] if 'dbVariable' in conf else 'db'
    conf['tableNamePrefix'] = conf['tableNamePrefix'] if 'tableNamePrefix' in conf else None
    conf['tables'] = conf['tables'] if 'tables' in conf else None
    conf['exclude'] = conf['exclude'] if 'exclude' in conf else None
    conf['toCamelCase'] = conf['toCamelCase'] if 'toCamelCase' in conf else True
    conn = check_and_connect(conf)
    tables = get_all_tables(conn)
    write_entities(conn, tables, conf)
    conn.close()
