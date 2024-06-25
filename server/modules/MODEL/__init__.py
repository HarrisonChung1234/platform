import os
import flask
from flask import request, jsonify,make_response
import json
# import cv2
from ..DB import initialize
from modules.main import model_train,detect
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity

class ModelAPI:
    def __init__(self):
        self.blueprint = flask.Blueprint('model', __name__, url_prefix='/model')
        self.blueprint.add_url_rule('/train', view_func=self.train_model, methods=['POST', 'GET'])
        self.blueprint.add_url_rule('/detect', view_func=self.detect_flk, methods=['POST', 'GET'])
        
    @jwt_required()
    def train_model(self):
        """
        本函数用于根据用户提供的数据集来训练
        请求地址: http://127.0.0.1:5000/model/train
        POST:
            ds_name: 训练集
            model: 模型种类
            return: 
            {'message': 'Train successfully'}
        GET:
        :return:
        jsonify(name)
        name 是所有数据集的名称
        """
        if request.method == 'POST':
            username = get_jwt_identity()
            ds_name = request.json.get('ds_name')
            service = request.json.get('service')
            model = request.json.get('model')
            p_set = request.json.get('p_set')
            p_name = request.json.get('p_name')
            # docker_command = [
            #     'sudo docker run test2:latest'
            # ]
            # TODO:
        if request.method == 'GET':
            username = get_jwt_identity()
            db = initialize('127.0.0.1', '5432', 'postgres', 'postgres', '123456')
            result = list(db.get_all_dataset_path(username))
            name = [x[0] for x in result]
            return jsonify(name)
        
    @jwt_required()
    def detect_flk(self):
        """
        本函数用于调用model来检测用户的数据集
        请求地址: http://127.0.0.1:5000/model/detect
        POST:
            model_name: 训练集
            model_type: 模型种类
            p_set: 用户要检测的图片集
            p_name: 照片名
            :return: jsonify({'message': 'Detect successfully'})
        GET:
            step == '1':
                :return : jsonify(name) name 是所有数据集的名称
            step == '2':
                ds_name : 用户选中的照片集名称
                :return:
                error: jsonify({'error': 'Invalid request'}), 500
                success: response_msg = {
                    'state': 'success',
                    'dataset_name': ds_name,
                    'image_count': image_count,
                    'image_names': image_names
                }
        """
        if request.method == 'POST':
            username = get_jwt_identity()
            model_name = request.json.get('model_name')  # 需要调用哪个数据集对应的model
            model_type = request.json.get('model_type')  # 需要调用的模型类型
            p_set = request.json.get('p_set')
            p_name = request.json.get('p_name')
            # TODO:
            model_path = "/home/ubuntu/platform/server/modules/MODEL"
            src_path = "/home/ubuntu/platform/server/modules/Dataset/workspace/asd/PCB/PCB/Images/000000.jpg"
            
            device = 'cpu'
            db = initialize('127.0.0.1', '5432', 'postgres', 'postgres', '123456')
            # db.load_model(username, model_name, model_type, model_path)
            db.get_single_pic(username, p_set, p_name, src_path)
            model_path += '/pretrained/yolov5m.pt'
            img_stream = detect(model_path, device, src_path)
            # img_stream = ''
            import base64
            import time
            time.sleep(10)
            response_msg = {
                "message": "Detect successfully",
                "img" : img_stream
            }
            return jsonify(img_stream)
        if request.method == 'GET':
            # print('a')
            step = request.args.get('step')
            if step == '1':
                # print('ab')
                username = get_jwt_identity()
                db = initialize('127.0.0.1', '5432', 'postgres', 'postgres', '123456')
                result = db.get_all_dataset_path(username)
                name = [x[0] for x in result]
                # print('b')
                return jsonify(name)
            if step == '2':
                username = get_jwt_identity()
                db = initialize('127.0.0.1', '5432', 'postgres', 'postgres', '123456')
                ds_name = request.args.get('ds_name')
                result = dict(db.get_all_dataset_path(username))
                dir_path = result[ds_name]
                print(dir_path)
                coco_path = os.path.join(dir_path, 'sample-obj-dct-annotated-coco/Annotations/coco_info.json')
                if not os.path.exists(coco_path):
                    make_response(jsonify({'error': 'Invalid request'}), 500)
                with open(coco_path,'r') as file:
                    anno = json.load(file)
                    image_count = len(anno['images'])
                    image_names = []
                    for image in anno['images']:
                        name = image['file_name']
                        if id not in anno['images_deleted']:
                            image_names.append(name)
                response_msg = {
                    'state': 'success',
                    'dataset_name': ds_name,
                    'image_count': image_count,
                    'image_names': image_names
                }
                return jsonify(response_msg)
            
    def get_blueprint(self):
        return self.blueprint