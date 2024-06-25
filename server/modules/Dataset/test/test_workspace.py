import unittest
import requests
import json

class TestDataset(unittest.TestCase):

    def test(self):
        session = requests.Session()
        # 先进行登录
        url = "http://127.0.0.1:5000/User/login"
        json_file = {'username': 'abc',
                     'password': '123456'}
        response = session.post(url, json=json_file)
        print(response.json())
        # 判断响应是否成功（根据实际情况进行断言）
        self.assertEqual(response.status_code, 200)

        # 测试工作区
        url = "http://127.0.0.1:5000/Dataset/workspace"
        response = session.get(url)
        # print(response.text)
        # print(response.json())
        # # 判断响应是否成功（根据实际情况进行断言）
        self.assertEqual(response.status_code, 200)

        # url = "http://127.0.0.1:5000/Dataset/transfer"
        # file_path = "./target_sfid.zip"
        # chunk_size = 2048000  # 设置分块大小为 2MB
        # cnt = -1
        # is_end = 0

        # # 测试文件上传至工作区
        # with open(file_path, "rb") as file:
        #     while True:
        #         chunk = file.read(chunk_size)
        #         if not chunk:
        #             break

        #         is_end = int(not bool(file.peek(chunk_size)))
        #         print('is_end:', is_end)
        #         cnt = cnt + 1

        #         # 将当前块的内容作为分块上传的一部分
        #         files = {'file': chunk}
        #         meta = {'proc_type': 'upload_ws', 
        #                 'filename': 'test',
        #                 'chunk_idx': f'{cnt}',
        #                 'is_end': f'{is_end}'}  # JSON 数据
        #         data = {'meta': json.dumps(meta)}
        #         response = session.post(url, files=files, data=data)

        #         # 判断响应是否成功（根据实际情况进行断言）
        #         self.assertEqual(response.status_code, 200)
        
        # # 测试工作区
        # url = "http://127.0.0.1:5000/Dataset/workspace"
        # response = session.get(url)
        # print(response.json())
        # # 判断响应是否成功（根据实际情况进行断言）
        # self.assertEqual(response.status_code, 200)

        session.close()
        
if __name__ == '__main__':
    unittest.main()