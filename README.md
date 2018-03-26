# sqlalchemy-mysql-generator
一个可以为Flask_SQLAlchemy创建Mysql数据库表对应的实体类的简单项目。

A simple project written in python, which can automatically generate Python classes according to Mysql databse tables. 

## 使用方法 Usage
    git clone git@github.com:wangyingsm/sqlalchemy-mysql-generator.git
    sudo pip install pymysql
    python autogen.py test.json

## JSON配置文件 JSON Config File
| 配置项 Configuration | 配置内容 Description |
| :-: | :- |
| host | Mysql server, default: localhost|
| user | Mysql username, default: root |
| password | Mysql password, default: '' |
| database | Mysql database default: 'test' |
| output | Python class files directories (will be created if not exists), default: $PWD/out_entities |
| dbModule | Python module name where flask_sqlalchemy db variable lies in, default: app |
| dbVariable | flask_sqlalchemy db variable name, default: db |
| tableNamePrefix | a list of prefix if you want to remove from table name, default: None |
| tables | a list of table names will be generated into Python classes, default: None |
| exclude | a list of table name will NOT be genarated into Python classes, default: None |
| toCamelCase | a boolean configuration shows if the table name or column name will be transformed into camel case, default: True |

