import os
import re
import json
import shutil
import zipfile

from flask_jwt_extended import get_jwt_identity
from flask import request
from functools import wraps

from .configs import *
 

def workspace_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        """
        一个检查工作区是否就绪的装饰器
        检查用户工作区目录是否存在, 若不存在就创建一个
        """
        username = get_jwt_identity()
        ws_path = os.path.join(WORKSPACE_PATH, username)
        if not os.path.exists(ws_path):
            os.makedirs(ws_path)
        return func(*args, **kwargs)
    return wrapper


def create_coco(username, dataset_name):
    """
    创建一个空的coco格式数据集

    :param username: 用户名称
    :param dataset_name: 数据集名称
    :return: None
    """

    # 在用户的upload目录中创建一个空的数据库
    ds_dir = os.path.join(UPLOAD_DIRECTORY, username, dataset_name)
    os.makedirs(ds_dir)
    img_dir = os.path.join(UPLOAD_DIRECTORY, IMAGE_DIRECTORY)
    os.makedirs(img_dir)
    anno_dir = os.path.join(UPLOAD_DIRECTORY, ANNOTATION_DIRECTORY)
    os.makedirs(anno_dir)
    anno_path = os.path.join(anno_dir, ANNOTATION_FILE)
    with open(anno_path, 'w') as file:
        coco_data = {
            'type': "instances",
            'info': {},
            'licenses': [],
            'images': [],
            'annotations': [],
            'categories': [],
            'images_deleted': [],
            'annotations_deleted': []
        }
        json.dump(coco_data, file, indent=4)

    # with open(os.path.join(WORKSPACE_PATH, username, 'info.json'), 'w') as file:
    #     info_data = {
    #         'dataset_name': dataset_name,
    #         'image_directory': img_dir,
    #         'annotation_directory': anno_dir,
    #     }
    #     json.dump(info_data, file, indent=4)

    # 将创建好的空的数据库传入用户数据库
    from ..DB import initialize
    db = initialize('127.0.0.1', '5432', 'postgres', 'postgres', '123456')
    db.save_data(username, dataset_name, ds_dir)
    # 清空当前用户的数据库暂存区
    shutil.rmtree(os.path.join(UPLOAD_DIRECTORY, username))
    # 结束与数据库的连接
    db.disconnect()


def upload_ws(username, meta):
    """
    将数据集从前端上传至后端工作区

    :param username: 进行操作的用户名称
    :param meta: 存储操作需要的各种参数
    """
    print(meta)
    chunk = request.files.get('file')
    chunk_index = int(meta['chunk_idx'])
    filename = meta['filename']
    num = int(meta['num'])
    flag = dataset_upload(chunk, chunk_index, filename, username, num)

    if not flag:
        response_msg = {'state': 'success', 'chunk_index': chunk_index}

    else:
        ds_path = dataset_merge(num, filename, username)
        # print(ds_path)

        ds_info = {}
        ds_info['dataset_name'] = filename
        # 将数据集的图片、标注文件路径记录在一个json文件里
        for dir, dirnames, filenames in os.walk(ds_path):
            img_dir = os.path.join(dir, IMAGE_DIRECTORY)
            if not os.path.exists(img_dir) or not os.path.isdir(img_dir):
                continue
            ds_info['image_directory'] = img_dir
        for dir, dirnames, filenames in os.walk(ds_path):
            anno_dir = os.path.join(dir, ANNOTATION_DIRECTORY)
            if not os.path.exists(anno_dir) or not os.path.isdir(anno_dir):
                continue
            ds_info['annotation_directory'] = anno_dir
            # print(anno_dir)
            
        anno_path = os.path.join(ds_info['annotation_directory'], ANNOTATION_FILE)
        with open(anno_path, 'r') as file:
            anno = json.load(file)
            anno['images_deleted'] = []
            anno['annotations_deleted'] = []
        with open(anno_path, 'w') as file:
            json.dump(anno, file, indent=4)

        with open(os.path.join(WORKSPACE_PATH, username, WORKSPACE_INFO_FILENAME), 'w') as file:
            json.dump(ds_info, file, indent=4)
        
        response_msg = {'state': 'success'}
    
    return response_msg

# def upload_db(username, meta):
#     """
#     将工作区中的某一数据集传给数据库

#     :param username: 进行操作的用户名称
#     :param meta: 存储操作需要的各种参数
#     """
#     from ..DB import initialize
#     filename = meta['filename']
#     # 连接数据库
#     db = initialize('127.0.0.1', '5432', 'postgres', 'postgres', '123456')
#     db.save_data(username, filename, file_path)

#     response_msg = {'state': 'success'}
#     return response_msg
    
#     response_msg = {'state': f'error: filename {filename} did not exist'}
#     return response_msg


def dataset_upload(chunk, chunk_index, filename, username, num):
    """
    该函数接收前端传来的分块数据集，暂存在工作区

    :param chunk: 文件块
    :param chunk_index: 文件块下标
    :param filename: 文件名
    :return: 包含传输状态的json文件
    """

    # 创立缓存目录
    temp_dir = f'./modules/Dataset/upload/{username}'
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    # 分块缓存
    chunk.save(f'./modules/Dataset/upload/{username}/{filename}_{chunk_index}')

    # 检查块数是否满足要求
    pattern = re.compile(rf'{filename}_\d+')
    file_list = os.listdir(temp_dir)
    count = 0
    for file in file_list:
        if pattern.match(file):
            count += 1

    if count == num:
        return True
    else:
        return False


def dataset_merge(num, filename, username):
    """
    该函数合并文件分块

    :param filename: 文件名
    :param chunk_size: 文件块个数
    :return: 包含合并成功与否的json文件
    """
    # 合并文件块
    user_path = f'./modules/Dataset/upload/{username}'
    chunk_paths = [os.path.join(user_path, f'{filename}_{i}') for i in range(num)]
    file_path = f'./modules/Dataset/upload/{username}/{filename}.zip'
    with open(file_path, 'wb') as f:
        for chunk_path in chunk_paths:
            with open(chunk_path, 'rb') as chunk_file:
                f.write(chunk_file.read())
            os.remove(chunk_path)
    
    # 解压文件
    with zipfile.ZipFile(file_path, 'r') as file:
        # 解压目录为用户自定义的文件名目录下
        destination_path = os.path.join(user_path, f'{filename}')
        if not os.path.exists(destination_path):
            os.makedirs(destination_path)
        file.extractall(destination_path)
    os.remove(file_path)
    
    # 返回合并后的文件路径
    return destination_path
    