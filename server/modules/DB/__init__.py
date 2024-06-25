import flask
from .pgdb import PostgreSQLDatabase

class DatabaseAPI:
    def __init__(self):
        self.blueprint = flask.Blueprint('DB', __name__, url_prefix='/DB')
    
    def get_blueprint(self):
        return self.blueprint
    
def initialize(host, port, db_name, user, password):
    """
    初始化并连接数据库

    :param host: 数据库所在服务器ip
    :param port: 服务器端口
    :param db_name: 数据库名称
    :param user: 用户名
    :param password: 密码
    :return: 数据库实例
    """
    db = PostgreSQLDatabase(host, port, db_name, user, password)
    db.connect()
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        password VARCHAR(50) NOT NULL,
        path VARCHAR(100) NOT NULL
    );
    '''
    db.execute_query(create_table_query)

    return db
