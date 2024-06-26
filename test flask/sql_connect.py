# 这是第一种
# from flask import Flask
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
#
# app = Flask(__name__)
#
#
# @app.route('/')
# def hello():
#     # 创建数据库引擎
#     from sqlalchemy import text
#     engine = create_engine('mysql://root:root@127.0.0.1/test')
#
#     # 创建Session对象
#     Session = sessionmaker(bind=engine)
#     session = Session()
#
#     # 执行SQL语句
#     result = session.execute(text("SELECT * FROM test1"))
#
#     # 处理查询结果
#     for row in result:
#         print(row)
#
#     # 关闭会话
#     session.close()
#
#     return 'hello world'
#
# if __name__ == '__main__':
#     app.run(port=5000, debug=True)


# 这是第二种
# import hashlib
# import pymysql
#
# # def md5_salt_encrypt(password, salt):
# #     # 在密码末尾添加盐
# #     salted_password = password + salt
# #     # 创建MD5对象
# #     md5_obj = hashlib.md5()
# #     # 更新MD5对象的内容
# #     md5_obj.update(salted_password.encode('utf-8'))
# #     # 获取加密后的结果
# #     encrypted_password = md5_obj.hexdigest()
# #     return encrypted_password
#
# def connect():
#     db = pymysql.connect(
#         host='127.0.0.1',    # 数据库主机地址
#         user='root',        # 用户名
#         password='root',    # 密码
#         database='test'        # 数据库名
#     )
#     return db
#
# def close(db):
#     db.close()
#
# def command(db, command):
#     cursor = db.cursor()
#     cursor.execute(command)
#     db.commit()
#     data = cursor.fetchall()
#     return data
#
# def check(username, password):
#     db = connect()
#     ret = command(db, "select * from test3 where username = '{}'".format(username))
#     if len(ret) == 0:
#         print("check not passed")
#     else:
#         # md5_password = md5_salt_encrypt(user, password)
#         if ret[0][1] != password:
#             print("check not passed")
#         else:
#             print("login successful!")
#     close(db)
#
# def check_if_exists(username):
#     db = connect()
#     cmd = "select * from test3 where username = '{}'".format(username)
#     ret = command(db, cmd)
#     close(db)
#     return ret
#
# def register(username, password):
#     check_result = check_if_exists(username)
#     if len(check_result) != 0:
#         print("already register!")
#     else:
#         db = connect()
#         # md5_password = md5_salt_encrypt(user, password)
#         cmd = "insert into test3 values('{}', '{}');".format(username, password)
#         ret = command(db, cmd)
#         close(db)
#
# def delete(user):
#     db = connect()
#     cmd = "delete from test3 where username='{}';".format(user)
#     ret = command(db, cmd)
#     close(db)
#
# # register('hkbin', '123')
# # delete('test')
#
#
# # db = connect()
# # cmd = "select * from test3;"
# # ret = command(db, cmd)
# # print(ret)
# delete('hkbin')
# # close(db)
#
