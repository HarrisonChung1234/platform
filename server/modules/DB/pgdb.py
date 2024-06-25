import psycopg2
import shutil

# import sshtunnel


class PostgreSQLDatabase:
    """
    PostgreSQL数据库管理类
    """
    def __init__(self, host, port, database, user, password):
        """
        数据库初始化函数

        :param host: 服务器ip
        :param port: 端口
        :param database: 数据库名称
        :param user: 用户名
        :param password: 密码
        """
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
        self.cursor = None

    def connect(self):
        """
        该函数用于连接数据库
        """
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            self.cursor = self.connection.cursor()
            print("Connected to the PostgreSQL database.")
        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL:", error)

    def disconnect(self):
        """
        该函数用于断连数据库
        """
        if self.connection:
            self.cursor.close()
            self.connection.close()
            print("Disconnected from the PostgreSQL database.")

    def execute_query(self, query):
        """
        该函数用于执行传进来的数据库指令

        :param query: 语句
        """
        try:
            self.cursor.execute(query)
            self.connection.commit()
            print("Query executed successfully.")
        except (Exception, psycopg2.Error) as error:
            print("Error while executing the query:", error)

    def fetch_data(self, query):
        """
        该函数用于获取用户信息

        :param query: 语句
        """
        try:
            self.cursor.execute(query)
            result = self.cursor.fetchone()
            self.connection.commit()
            return result
        except (Exception, psycopg2.Error) as error:
            print("Error while fetching data from the database:", error)
            return []
        
    def register(self, username):
        """
        该函数用于用户注册创建新表

        :param username: 当前的username
        """
        try:
            self.connect()
            create_table_query = 'CREATE TABLE IF NOT EXISTS ' + username + ' (ds_name VARCHAR(100) UNIQUE NOT NULL,path VARCHAR(100) NOT NULL);'
            self.execute_query(create_table_query)
        except (Exception, psycopg2.Error) as error:
            print("Error while the registeration:", error)
            return []

    def save_data(self, username, ds_name, path):
        """
        该函数用于将文件储存进数据库

        :param username: 当前的username
        :param ds_name: 当前需要保存的数据集的名字
        :param path: 需要存储的文件的路径
        """
        query = "SELECT * FROM users WHERE username = '" + username + "';"
        try:
            user = self.fetch_data(query)
            if user:
                db_path = user[3] + '/' + ds_name
                query = "INSERT INTO " + username + " (ds_name, path) VALUES ( '" + ds_name + "', '" + db_path + "');"
                import os
                if os.path.exists(db_path):
                    shutil.rmtree(db_path)
                shutil.copytree(path, db_path)
                self.execute_query(query)
        except (Exception, psycopg2.Error) as error:
            print("Error while moving data to the database:", error)
            return []
        
    def get_all_dataset_path(self, username):
        """
        该函数用于取出当前用户已有的数据集路径

        :param username: 当前的username
        """
        try:
            self.connect()
            query = "SELECT * FROM " + username + ";"
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            return result
        except (Exception, psycopg2.Error) as error:
            print("Error while fetching dataset_path from the database:", error)
            return []


    def get_data(self, username, ds_name, path):
        """
        该函数用于将文件取出数据库

        :param username: 当前的username
        :param ds_name: 需要的dataset的名字
        :param path: 需要放置的文件的路径
        """
        query = "SELECT * FROM users WHERE username = '" + username + "';"
        try:
            user = self.fetch_data(query)
            print(query)
            if user:
                db_path = user[3] + '/' + ds_name
                import os
                print(os.path.join(path,ds_name))
                if os.path.exists(os.path.join(path,ds_name)):
                    shutil.rmtree(os.path.join(path,ds_name))
                shutil.copytree(db_path, os.path.join(path,ds_name))
        except (Exception, psycopg2.Error) as error:
            print("Error while moving data from the database:", error)
            return []

    def get_single_pic(self, username, db_name, p_name, path):
        """
        该函数用于将单张图片取出数据库

        :param username: 当前的username
        :param db_name: 当前的用户的数据集的名字
        :param p_name: 当前pic的名字
        :param path: 需要存储的文件的路径
        """
        query = "SELECT * FROM users WHERE username = '" + username + "';"
        try:
            user = self.fetch_data(query)
            if user:
                db_path = user[3] + '/' + db_name + '/' + 'sample-obj-dct-annotated-coco' + '/' + 'Images' + '/' + p_name
                shutil.copyfile(db_path, path)
        except (Exception, psycopg2.Error) as error:
            print("Error while moving one single pic from the database:", error)
            return []

    def save_model(self, username, db_name, path):
        """
        该函数用于将训练好的model存进数据库

        :param username: 当前的username
        :param db_name: 当前的用户的数据集的名字
        :param path: 需要存储的文件的当前路径
        """
        query = "SELECT * FROM users WHERE username = '" + username + "';"
        try:
            user = self.fetch_data(query)
            if user:
                db_path = user[3] + '/' + db_name
                shutil.copyfile(path, db_path)
        except (Exception, psycopg2.Error) as error:
            print("Error while saving the model to the database:", error)
            return []

    def save_the_label(self, username, db_name, p_set, f_name, path):
        """
        该函数用于将单张图片的标注文件存进数据库

        :param username: 当前的username
        :param db_name: 当前的用户的数据集的名字
        :param p_set: 属于当前数据集里面的哪个集合 (e.g train, test)
        :param p_name: 当前标注文件的名字
        :param path: 需要存储的文件的当前路径
        """
        query = "SELECT * FROM users WHERE username = '" + username + "';"
        try:
            user = self.fetch_data(query)
            if user:
                db_path = user[3] + '/' + db_name + '/' + p_set + '/' + f_name
                shutil.copyfile(path, db_path)
        except (Exception, psycopg2.Error) as error:
            print("Error while saving the label to the database:", error)
            return []

    def load_model(self, username, db_name, model_name, path):
        """
        该函数用于将训练好的model存进数据库

        :param username: 当前的username
        :param db_name: 当前的用户的数据集的名字
        :param model_name: 当前的用户的model的名字
        :param path: 需要存储的文件的当前路径
        """
        query = "SELECT * FROM users WHERE username = '" + username + "';"
        try:
            user = self.fetch_data(query)
            if user:
                db_path = user[3] + '/' + db_name + '/' + model_name
                shutil.copytree(db_path, path)
        except (Exception, psycopg2.Error) as error:
            print("Error while loading the model to the database:", error)
            return []
    
    def delete_data(self, username, ds_name):
        """
        该函数用于删除用户用户的指定数据集

        :param username: 当前的username
        :param ds_name: 需要删除的数据集的名字
        """
        query = "DELETE FROM " + username + " WHERE " + "ds_name='" + ds_name + "';";
        try:
            query_path = "SELECT path FROM " + username + " WHERE " + "ds_name = '" + ds_name + "';";
            print(query_path)
            path = self.fetch_data(query_path)
            print(path)
            import os
            if os.path.exists(path[0]):
                shutil.rmtree(path[0])
                self.execute_query(query)
        except (Exception, psycopg2.Error) as error:
            print("Error while deleting the dataset from the database:", error)
            return []
