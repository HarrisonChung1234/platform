from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
# 从modules引入组件

from modules import Dataset
from modules import DB
from modules import User
from modules import MODEL

if __name__ == '__main__':
    # flask主体程序声明
    app = Flask(__name__)
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 86400
    CORS(app, supports_credentials=True)    # 跨域
    jwt = JWTManager(app)
    app.secret_key = 'secret!'
    app.config['JWT_SECRET_KEY'] = 'secret!'
    User_object = User.UserAPI()
    Model_object = MODEL.ModelAPI()
    DB_object = DB.DatabaseAPI()
    Dataset_object = Dataset.DatasetAPI()
    # 注册蓝图
    app.register_blueprint(Dataset_object.get_blueprint())
    app.register_blueprint(DB_object.get_blueprint())
    app.register_blueprint(User_object.get_blueprint())
    app.register_blueprint(Model_object.get_blueprint())
    
    # 连接并获取数据库实例
    # app.db = DB.initialize('127.0.0.1', '5432', 'postgres', 'postgres', '123456')

    # 运行项目
    app.run(host='0.0.0.0', debug=True)
    # app.run(debug=True)
