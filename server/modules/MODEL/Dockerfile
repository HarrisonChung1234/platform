FROM nvidia/cuda:11.1.1-base-ubuntu20.04
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo '$TZ' > /etc/timezone
RUN mkdir -p /home/ubuntu/platform/server/modules/Dataset/workspace
RUN chown -R root:root /home/ubuntu/platform/server/modules/Dataset/workspace
COPY main.py /home/ubuntu/platform/server/modules/Dataset/workspace
COPY yolov5 /home/ubuntu/platform/server/modules/Dataset/workspace
ADD main.py /home/ubuntu/platform/server/modules/Dataset/workspace
ADD yolov5 /home/ubuntu/platform/server/modules/Dataset/workspace
COPY requirements.txt /home/ubuntu/platform/server/modules/Dataset/workspace
RUN \
    sed -i "s@http://.*archive.ubuntu.com@https://mirrors.tuna.tsinghua.edu.cn@g" /etc/apt/sources.list \
    && sed -i "s@http://.*security.ubuntu.com@https://mirrors.tuna.tsinghua.edu.cn@g" /etc/apt/sources.list \
    && apt-get clean && apt-get update \
    && apt-get install --assume-yes apt-utils \
    && apt-get install -y build-essential \
    && apt-get install -y unzip \
    && apt-get install -y xz-utils \
    && apt-get install -y curl \
    && apt-get install -y libseccomp-dev build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev wget libbz2-dev \
    && apt-get update && apt-get install -y python3.9 python3.9-dev python3-pip \
    && ln -s /usr/bin/python3.9 /usr/bin/python
	
RUN \
    pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple --default-timeout=10000  \
    && pip install -r /home/ubuntu/platform/server/modules/Dataset/workspace/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir --default-timeout=10000 \
    && pip install bert4keras==0.10.7 -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir --default-timeout=10000 \
    && apt-get remove -y build-essential && apt-get clean \
    && apt update && apt install libgl1-mesa-glx -y \
    && apt-get install libglib2.0-dev -y \
    && apt-get install libglib2.0 -y \
    && apt-get update
EXPOSE 7000

WORKDIR '/home/ubuntu/platform/server/modules/Dataset/workspace'
# CMD ['python /home/ubuntu/platform/server/modules/yolov5/train.py 
#             --data /home/ubuntu/platform/server/modules/yolov5/data/my_data.yaml 
#             --cfg /home/ubuntu/platform/server/modules/yolov5/models/yolov5m.yaml
#             --weights /home/ubuntu/platform/server/modules/yolov5/pretrained/yolov5m.pt
#             --epoch 5000
#             --batch-size 4
#             --device cuda
#             --name exp_flask_test1']
ENTRYPOINT ["python3","train.py"]
