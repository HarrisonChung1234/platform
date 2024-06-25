import os
import io
import shutil
import json
import threading
from PIL import Image

from flask import Blueprint
from flask import request
from flask import jsonify
from flask import make_response
from flask import send_file
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity

from .configs import *
from .utils import *

class DatasetAPI:
    def __init__(self):
        self.blueprint = Blueprint('Dataset', __name__, url_prefix='/Dataset')
        self.chunk_lock = threading.Lock()
        self._register_routes()
    
    def _register_routes(self):
        self.blueprint.route('/workspace', methods=['GET'])(jwt_required()(workspace_required(self.homepage)))
        self.blueprint.route('/create', methods=['POST'])(jwt_required()(workspace_required(self.dataset_create)))
        self.blueprint.route('/upload', methods=['POST'])(jwt_required()(workspace_required(self.upload)))
        self.blueprint.route('/workspace/image/<int:id>', methods=['GET'])(jwt_required()(workspace_required(self.get_image)))
        self.blueprint.route('/workspace/image-attribute/<int:id>', methods=['GET'])(jwt_required()(workspace_required(self.get_image_attribute)))
        self.blueprint.route('/workspace/annotation/<int:id>', methods=['GET'])(jwt_required()(workspace_required(self.get_annotation)))
        self.blueprint.route('/workspace/modify', methods=['POST'])(jwt_required()(workspace_required(self.modify)))
        self.blueprint.route('/workspace/modify-annotation', methods=['POST'])(jwt_required()(workspace_required(self.modify_annotation)))
        self.blueprint.route('/user', methods=['GET'])(jwt_required()(self.get_user_datasets_info))
        self.blueprint.route('/load', methods=['POST'])(jwt_required()(workspace_required(self.load_dataset)))
        self.blueprint.route('/save', methods=['POST'])(jwt_required()(workspace_required(self.save_dataset)))
    
    def homepage(self):
        """
        工作区首页

        :return: json => state: 当前工作区是否存在数据集, failed为不存在, success为存在
                        dataset_name: 数据集名称
                        image_count: 图片数量
                        image_ids: 一个列表, 存储所有图片的id信息
                        categories: 数据集的类别信息
        """
        if request.method == 'GET':
            # 查询当前用户的工作区信息
            # 如果当前用户的工作区目录未创建则创建一个
            # 返回工作区存储的数据集信息
            username = get_jwt_identity()
            ws_path = os.path.join(WORKSPACE_PATH, username)
            os.makedirs(ws_path, exist_ok=True)
            ws_info = os.path.join(ws_path, WORKSPACE_INFO_FILENAME)
            if not os.path.exists(ws_info):
                response_msg = {
                    'state': 'failed'
                }
            else:
                # 工作区中已有数据集时返回数据集信息
                # 返回的数据集信息包括数据集名称、图片数量、所有图片id、类别信息
                with open(ws_info, 'r') as file:
                    info = json.load(file)
                    dataset_name = info['dataset_name']
                    # dataset_format = info['dataset_format']
                    anno_dir = info['annotation_directory']
                    anno_path = os.path.join(anno_dir, ANNOTATION_FILE)
                
                # 获取图片id、图片数量和类别信息
                with open(anno_path, 'r') as file:
                    anno = json.load(file)
                    image_count = len(anno['images'])
                    categories = []
                    image_ids = []

                    for image in anno['images']:
                        id = image['id']
                        if str(id) not in anno['images_deleted']:
                            image_ids.append(id)

                    for category in anno['categories']:
                        id = category['id']
                        if str(id) not in anno['categories_deleted']:
                            categories.append(category)

                response_msg = {
                    'state': 'success',
                    'dataset_name': dataset_name,
                    'image_count': image_count,
                    'image_ids': image_ids,
                    'categories': categories
                }

            return jsonify(response_msg)
        
    def dataset_create(self):
        """
        根据传递进来的信息建立一个空的数据集

        :return: json => state: 执行成功与否的标志 
        """
        if request.method == 'POST':
            username = get_jwt_identity()
            dataset_name = request.json.get('dataset_name')
            fmt = request.json.get('format')

            # 创建一个coco格式的数据集
            if fmt == 'coco':
                create_coco(username, dataset_name)

                response_msg = {
                    'state': 'success'
                }
                return jsonify(response_msg)
    
    def upload(self):
        """
        该函数根据请求的操作类型决定调用的数据集处理函数
        只支持zip格式的coco数据集文件传输
        POST
        请求参数: 
            1.操作upload_ws: file(以表单form提交), meta(一个json格式的表单项, 包括: proc_type, chunk_idx, filename, num)
            2.操作upload_db: 一个表单项proc_type
        参数说明:
            file: 文件分块
            meta: 该属性的内容为json格式的字符串
            proc_type: 要进行的操作类型, 目前已实现的有2种(upload_ws->将数据集上传至workspace, upload_db->将数据集从工作区上传至数据库)
            chunk_idx: 当前传递的文件分块的序号, 从0开始编号
            filename: 要传递的数据集名称
            is_end: 当前分块是否为最后一块, 若为最后一块此项的值为1, 否则为0
        请求地址: http://114.132.184.220:5000/Dataset/transfer

        :return: json文件, 包含一个state, 用来记录当前操作结果为成功还是错误, 错误时会返回错误描述
        """

        if request.method == 'POST':       
            # 获取当前登录用户名
            username = get_jwt_identity()
            print(username)
            # TODO: 考虑增加当前未登录时的处理操作
            meta = request.form.get('meta')
            meta = json.loads(meta)
            proc_type = meta['proc_type']

            # 将数据集从前端上传至后端数据库
            if proc_type == 'upload_db':
                with self.chunk_lock:
                    # response_msg = upload_ws(username, meta)
                    chunk = request.files.get('file')
                    chunk_index = int(meta['chunk_idx'])
                    filename = meta['filename']
                    num = int(meta['num'])
                    flag = dataset_upload(chunk, chunk_index, filename, username, num)

                    if not flag:
                        response_msg = {'state': 'success', 'chunk_index': chunk_index}

                    else:
                        ds_path = dataset_merge(num, filename, username)
                        # 连接数据库
                        from ..DB import initialize
                        db = initialize('127.0.0.1', '5432', 'postgres', 'postgres', '123456')
                        user_dir = os.path.join(UPLOAD_DIRECTORY, username)     
                        all_items = os.listdir(user_dir)
                        for path in all_items:
                            path = os.path.join(user_dir, path)
                            if os.path.isdir(path):
                                db.save_data(username, filename, path)
                                break
                        
                        # 清空当前用户的数据库暂存区
                        shutil.rmtree(os.path.join(UPLOAD_DIRECTORY, username))
                        # 结束与数据库的连接
                        db.disconnect()

                        response_msg = {'state': 'success'}

                return jsonify(response_msg)
            else:
                response_msg = {'state': 'error: invalid proc_type'}
                return make_response(jsonify(response_msg), 500)

    def get_image(self, id):
        """
        根据id获取图片
        """
        username = get_jwt_identity()
        info_path = os.path.join(WORKSPACE_PATH, username, WORKSPACE_INFO_FILENAME)
        with open(info_path, 'r') as file:
            info = json.load(file)
            image_dir = info['image_directory']
            anno_dir = info['annotation_directory']
        
        with open(os.path.join(anno_dir, ANNOTATION_FILE), 'r') as file:
            anno = json.load(file)
            for image in anno['images']:
                if image['id'] == id and str(id) not in anno['images_deleted']:
                    image_name = image['file_name']
                    image_path = os.path.join(image_dir, image_name)
        
        print(image_path)
        return send_file(image_path, mimetype='image/jpeg')
    
    def get_image_attribute(self, id):
        """
        根据id获取图片对应的信息
        """
        username = get_jwt_identity()
        info_path = os.path.join(WORKSPACE_PATH, username, WORKSPACE_INFO_FILENAME)
        with open(info_path, 'r') as file:
            info = json.load(file)
            anno_dir = info['annotation_directory']
        
        with open(os.path.join(anno_dir, ANNOTATION_FILE), 'r') as file:
            anno = json.load(file)
            for image in anno['images']:
                if image['id'] == id and str(id) not in anno['images_deleted']:
                    img_attr = image
                    break
        
        response_msg = {
            'state': 'success',
            'image_attribute': img_attr
        }
        return jsonify(response_msg)
    
    def get_annotation(self, id):
        """
        根据图片id获取图片的标注信息

        :param id: 图片id
        :return: json => state: 执行成功与否的标志
                        annotations: 存储图片标注信息的列表
        """
        if request.method == 'GET':
            username = get_jwt_identity()
            ws_info = os.path.join(WORKSPACE_PATH, username, WORKSPACE_INFO_FILENAME)
            with open(ws_info, 'r') as file:
                info = json.load(file)
                anno_dir = info['annotation_directory']
                anno_path = os.path.join(anno_dir, ANNOTATION_FILE)
            
            annotations = []
            with open(anno_path, 'r') as file:
                anno = json.load(file)
                for annotation in anno['annotations']:
                    if annotation['image_id'] == id:
                        annotations.append(annotation)
            
            response_msg = {
                'state': 'success',
                'annotations': annotations
            }
            return jsonify(response_msg)
        
    def modify(self):
        """
        增加或删除数据集中的图片或标注信息

        """
        username = get_jwt_identity()
        proc_type = request.form.get('proc_type')
        data_type = request.form.get('data_type')

        info_path = os.path.join(WORKSPACE_PATH, username, WORKSPACE_INFO_FILENAME)
        with open(info_path, 'r') as file:
            info = json.load(file)
            image_dir = info['image_directory']
            anno_dir = info['annotation_directory']

        if proc_type == 'add':
            # 增加图片
            response_msg = {
                'state': 'success'
            }
            
            if data_type == 'image':
                image = request.files.get('image')
                image_name = image.filename
                pil_image = Image.open(io.BytesIO(image.read()))
                width, height = pil_image.size
                pil_image.save(os.path.join(image_dir, image_name), 'JPEG', quality=90)

                with open(os.path.join(anno_dir, ANNOTATION_FILE), 'r') as file:
                    anno = json.load(file)
                    image_id = len(anno['images']) + 1
                    image_info = {
                        'file_name': image_name,
                        'height': height,
                        'width': width,
                        'id': image_id
                    }
                    anno['images'].append(image_info)
                response_msg['image_id'] = image_id
        
            # 增加标注
            elif data_type == 'annotation':
                annotation = request.form.get('annotation')
                annotation = json.loads(annotation)

                with open(os.path.join(anno_dir, ANNOTATION_FILE), 'r') as file:
                    anno = json.load(file)
                    annotation_id = len(anno['annotations']) + 1
                    annotation['id'] = annotation_id
                    anno['annotations'].append(annotation)
                response_msg['annotation_id'] = annotation_id
            
            # 增加类别
            elif data_type == 'category':
                category = request.form.get('category')
                category = json.loads(category)

                with open(os.path.join(anno_dir, ANNOTATION_FILE), 'r') as file:
                    anno = json.load(file)
                    category_id = len(anno['categories'])
                    category['id'] = category_id
                    anno['categories'].append(category)
                
                response_msg['category_id'] = category_id

        elif proc_type == 'delete':
            response_msg = {
                'state': 'success'
            }

            # 删除图片，同时删除图片对应的标注
            if data_type == 'image':
                id = request.form.get('id')
                with open(os.path.join(anno_dir, ANNOTATION_FILE), 'r') as file:
                    anno = json.load(file)
                    anno['images_deleted'].append(id)

                    for annotation in anno['annotations']:
                        if annotation['image_id'] == id:
                            anno['annotations_deleted'].append(annotation['id'])

            # 删除标注
            elif data_type == 'annotation':    
                id = request.form.get('id')
                with open(os.path.join(anno_dir, ANNOTATION_FILE), 'r') as file:
                    anno = json.load(file)
                    anno['annotations_deleted'].append(id)
                
            # 删除类别
            elif data_type == 'category':
                id = request.form.get('id')
                with open(os.path.join(anno_dir, ANNOTATION_FILE), 'r') as file:
                    anno = json.load(file)
                    anno['categories_deleted'].append(id)

        with open(os.path.join(anno_dir, ANNOTATION_FILE), 'w') as file:
            json.dump(anno, file, indent=4)

        return jsonify(response_msg)
    
    def modify_annotation(self):
        """
        修改标注
        """
        username = get_jwt_identity()
        image_id = request.form.get('image_id')
        annotations = json.loads(request.form.get('annotations'))
        print(annotations)

        info_path = os.path.join(WORKSPACE_PATH, username, WORKSPACE_INFO_FILENAME)
        with open(info_path, 'r') as file:
            info = json.load(file)
            anno_dir = info['annotation_directory']

        with open(os.path.join(anno_dir, ANNOTATION_FILE), 'r') as file:
            anno = json.load(file)
            i = 0
            while i < len(anno['annotations']):
                if str(anno['annotations'][i]['image_id']) == str(image_id):
                    del anno['annotations'][i]
                else:
                    i += 1
            anno['annotations'].extend(annotations)

        with open(os.path.join(anno_dir, ANNOTATION_FILE), 'w') as file:
            json.dump(anno, file, indent=4)
        
        response_msg = {
            'state': 'success'
        }
        return jsonify(response_msg)
    
    def get_user_datasets_info(self):
        """
        获取当前用户存储在数据库的所有数据集信息
        """
        username = get_jwt_identity()

        # 连接数据库
        from ..DB import initialize
        db = initialize('127.0.0.1', '5432', 'postgres', 'postgres', '123456')
        datasets_info = db.get_all_dataset_path(username)
        print(datasets_info)
        info = [dataset_info[0] for dataset_info in datasets_info]
        db.disconnect()

        response_msg = {
            'state': 'success',
            'info': info
        }
        return jsonify(response_msg)
    
    def load_dataset(self):
        """
        将指定数据集加载至工作区中
        """
        username = get_jwt_identity()
        dataset_name = request.form.get('dataset_name')
        print("dataset name:", dataset_name)

        # 连接数据库
        from ..DB import initialize
        db = initialize('127.0.0.1', '5432', 'postgres', 'postgres', '123456')
        ws_path = os.path.join(WORKSPACE_PATH, username)
        ds_path = os.path.join(ws_path, dataset_name)
        db.get_data(username, dataset_name, ws_path)

        ds_info = {}
        ds_info['dataset_name'] = dataset_name
        # 将数据集的图片、标注文件路径记录在一个json文件里
        print(ds_path)
        for dir, dirnames, filenames in os.walk(ds_path):
            img_dir = os.path.join(dir, IMAGE_DIRECTORY)
            print("img: ", img_dir)
            if not os.path.exists(img_dir) or not os.path.isdir(img_dir):
                continue
            ds_info['image_directory'] = img_dir
        for dir, dirnames, filenames in os.walk(ds_path):
            anno_dir = os.path.join(dir, ANNOTATION_DIRECTORY)
            print("anno: ", anno_dir)
            if not os.path.exists(anno_dir) or not os.path.isdir(anno_dir):
                continue
            ds_info['annotation_directory'] = anno_dir
            print(anno_dir)

        print(ds_info)    
        anno_path = os.path.join(ds_info['annotation_directory'], ANNOTATION_FILE)
        with open(anno_path, 'r') as file:
            anno = json.load(file)
            anno['images_deleted'] = []
            # anno['annotations_deleted'] = []
            anno['categories_deleted'] = []
        with open(anno_path, 'w') as file:
            json.dump(anno, file, indent=4)

        with open(os.path.join(WORKSPACE_PATH, username, WORKSPACE_INFO_FILENAME), 'w') as file:
            json.dump(ds_info, file, indent=4)

        response_msg = {'state': 'success'}
        return jsonify(response_msg)
    
    def save_dataset(self):
        """
        将工作区中的数据集保存至用户数据库
        :return:
        """
        username = get_jwt_identity()
        with open(os.path.join(WORKSPACE_PATH, username, WORKSPACE_INFO_FILENAME), 'r') as file:
            info = json.load(file)
            dataset_name = info['dataset_name']
            img_dir = info['image_directory']
            anno_dir = info['annotation_directory']

        with open(os.path.join(anno_dir, ANNOTATION_FILE), 'r') as file:
            anno = json.load(file)
            for id in anno['images_deleted']:
                for i, img in enumerate(anno['images']):
                    if str(img['id']) == id:
                        filename = img['file_name']
                        os.remove(os.path.join(img_dir, filename))
                        del anno['images'][i]
                        break    

            cnt = 1
            for i, img in enumerate(anno['images']):
                anno['images'][i]['id'] = cnt
                cnt += 1
            
            processed_annotations = []
            for i, annotation in enumerate(anno['annotations']):
                if str(annotation['image_id']) not in str(anno['images_deleted']):
                    processed_annotations.append(anno['annotations'][i])
            anno['annotations'] = processed_annotations
            
            cnt = 1
            for i, annotation in enumerate(anno['annotations']):
                anno['annotations'][i]['id'] = cnt
                cnt += 1

            for id in anno['categories_deleted']:
                for i, category in enumerate(anno['categories']):
                    if str(category['id']) == id:
                        del anno['categories'][i]
                        break   
            
            cnt = 1
            for i, category in enumerate(anno['categories']):
                anno['categories'][i]['id'] = cnt
                cnt += 1

            del anno['images_deleted']
            # del anno['annotations_deleted']
            del anno['categories_deleted']
        
        with open(os.path.join(anno_dir, ANNOTATION_FILE), 'w') as file:
            json.dump(anno, file, indent=4)

        # 连接数据库
        from ..DB import initialize
        db = initialize('127.0.0.1', '5432', 'postgres', 'postgres', '123456')
        all_items = os.listdir(os.path.join(WORKSPACE_PATH, username))
        for name in all_items:
            path = os.path.join(WORKSPACE_PATH, username, name)
            if os.path.isdir(path):
                dataset_name = name
                db.save_data(username, dataset_name, path)
                break

        # 清空工作区
        shutil.rmtree(os.path.join(WORKSPACE_PATH, username))
        # 结束与数据库的连接
        db.disconnect()

        response_msg = {'state': 'success'}
        return jsonify(response_msg)
    
    def delete_dataset(self):
        """
        删除用户目录中的数据集
        """
        username = get_jwt_identity()
        dataset_name = request.form.get('dataset_name')

        # 连接数据库
        from ..DB import initialize
        db = initialize('127.0.0.1', '5432', 'postgres', 'postgres', '123456')
        db.delete_data(username, dataset_name)
        # 结束与数据库的连接
        db.disconnect()

        response_msg = {'state': 'success'}
        return jsonify(response_msg)
    
    def get_blueprint(self):
        return self.blueprint

