import yaml
import os
from modules.yolov5.predict_func import detect_defect
from flask import current_app
def make_yaml(path):
    """
    根据传进的数据集进行构造yaml文件，为训练部分的模型提供导向
    :param path: 训练集文件夹路径 “data/targit_sfid”
    :return: 无返回，制作更新两个data.yaml文件和一个yolov5m.yaml文件
    """
    current_file_path = os.path.abspath(__file__)
    # 获取当前文件所在的目录
    parent_directory = os.path.dirname(current_file_path)
    # 获取上一级目录
    parent_directory = parent_directory.replace('\\', '/')
    yolo_path = parent_directory + '/yolov5'

    classes_path = path + "/classes.txt"
    with open(classes_path, 'r') as file:
        class_names = [line.strip() for line in file.readlines()]

    path_train = path + '/images/train'
    path_val = path + '/images/test'

    # 构建YAML数据
    data = {
        'train': path_train,
        'val': path_val,
        'nc': len(class_names),
        'names': class_names
    }

    # 将数据写入到yaml文件中
    yaml1 = path + r"/my_data.yaml"
    with open(yaml1, 'w') as file:
        yaml.dump(data, file)
    yaml2 = yolo_path + "/data/my_data.yaml"
    with open(yaml2, 'w') as file:
        yaml.dump(data, file)

    # 更新训练模型的yaml
    model_path = yolo_path + '/models/yolov5m.yaml'
    with open(model_path, 'r') as f:
        data_old = yaml.load(f, Loader=yaml.FullLoader)
    data_old['nc'] = len(class_names)
    with open(model_path, 'w') as f:
        yaml.dump(data_old, f)

def get_data_path(username, ds_name, path):
    db = current_app.db
    return db.get_data(username, ds_name, path)
    
def model_train(username, ds_name, device, epoch, batch_size, save_name):
    """
    训练模型
    :param username: client的名字
    :param ds_name: 数据集的名字
    :param device: 设备
    :param epoch:
    :param batch_size:
    :param save_name: 训练好的pt保存路径
    :return:
    """
    #TODO:
    path = "/data/platform/server/modules/Dataset/workspace/" + ds_name
    get_data_path(username, ds_name, path)
    current_file_path = os.path.abspath(__file__)
    # 获取当前文件所在的目录
    parent_directory = os.path.dirname(current_file_path)
    # 获取上一级目录

    make_yaml(path)
    yolo_path = parent_directory.replace('\\', '/') + '/yolov5'
    train_path = yolo_path + '/train.py'
    yaml_data_path = yolo_path + '/data/my_data.yaml'
    yaml_model_path = yolo_path + '/models/yolov5m.yaml'
    pretrain_path = yolo_path + '/pretrained/yolov5m.pt'
    os.system(f"python {train_path} --data {yaml_data_path} --cfg {yaml_model_path} --weights {pretrain_path} --epoch {epoch} --batch-size {batch_size} --device {device} --name {save_name}")
    res_path = yolo_path + '/runs/train/' + save_name
    return res_path

def detect(model_path, device, src_path):
    """
    单张图片的缺陷检测接口
    :param model_path: 模型存储的路径
    :param device:
    :param src_path: 待检测的图像路径
    :return:
    """
    res_path = detect_defect(model_path, device, src_path)
    return res_path


# 以下是一个简单的测试,先训练，再检测
# 注意检测完一张图片要及时保存在另一个文件夹，否则下次检测会将其覆盖
if __name__ == '__main__':
    path = "data/target_sfid" # 数据集路径
    device = 'cuda'
    epoch = 100
    batch_size = 4
    save_name = "exp_flask_test1"
    src_pic = 'E:/Track1-2G Track-400M/drive-download-20230325T145333Z-001/PCB_2/inference/000155.jpg'
    model_path = model_train(path, device, epoch, batch_size, save_name)
    best_model_path = model_path + "/weights/best.pt"
    res = detect(best_model_path, device, src_pic)


