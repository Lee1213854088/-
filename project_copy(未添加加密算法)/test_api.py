# import requests
# from flask import Flask, request
#
# app = Flask(__name__)
#
# @app.route('/api')
# def api():
#     url = 'http://43.139.249.124:5000/api'
#     headers = {'Content-Type': 'application/json'}
#     data = {'content': 'CA', 'user': 'hkbin'}
#
#     # 发送POST请求
#     response = requests.post(url, json=data, headers=headers)
#
#     # 打印返回的信息
#     print("Response:", response.json)
#
#
# if __name__ == '__main__':
#     # 启动 Flask 应用程序
#     app.run(host='0.0.0.0', port=5000)

# import requests
# import json
#
# url = 'http://43.139.249.124:5000/api'
# headers = {
#     "Content-Type": "application/json; charset=UTF-8",
#     "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36"
#     }
# data = {'content': 'CA', 'user': 'hkbin'}
#
# print(json.dumps(data))
# # 发送POST请求
# response = requests.post(url = url, data=json.dumps(data), headers = headers)
#
# # 打印返回的信息
# print(response)
# print("Response:", response.text)


import requests

url = "http://43.139.249.124:5000/api"
headers = {
    "Content-Type": "application/json",
}
data = {
    "content": "CA",
    "user": "hkbin",
}

response = requests.post(url, headers=headers, json=data)
# 输出响应的文本内容（可选）
print(response.text)



