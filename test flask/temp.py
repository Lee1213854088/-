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



from flask import Flask
from dataclasses import dataclass
from flask import render_template, request, url_for, redirect, session, g
import pymysql


app = Flask(__name__, static_url_path="/")
app.config['SECRET_KEY'] = "zx4c6ew1xzc4w65x5cwer4df"

def connect():
    db = pymysql.connect(
        host='127.0.0.1',    # 数据库主机地址
        user='root',        # 用户名
        password='root',    # 密码
        database='test'        # 数据库名
    )
    return db

def close(db):
    db.close()

def command(db, command):
    cursor = db.cursor()
    cursor.execute(command)
    db.commit()
    data = cursor.fetchall()
    return data

def check(username, password):
    db = connect()
    ret = command(db, "select * from test3 where username = '{}'".format(username))
    if len(ret) == 0:
        print("check not passed")
    else:
        # md5_password = md5_salt_encrypt(user, password)
        if ret[0][1] != password:
            print("check not passed")
        else:
            print("login successful!")
    close(db)

def check_if_exists(username):
    db = connect()
    cmd = "select * from test3 where username = '{}'".format(username)
    ret = command(db, cmd)
    close(db)
    return ret

def register(username, password):
    check_result = check_if_exists(username)
    if len(check_result) != 0:
        print("already register!")
    else:
        db = connect()
        # md5_password = md5_salt_encrypt(user, password)
        cmd = "insert into test3 values('{}', '{}');".format(username, password)
        ret = command(db, cmd)
        close(db)

def delete(user):
    db = connect()
    cmd = "delete from test3 where username='{}';".format(user)
    ret = command(db, cmd)
    close(db)

# register('hkbin', '123')
# delete('test')


db = connect()
cmd = "select * from test3;"
ret = command(db, cmd)
print(ret)
# close(db)


@dataclass
class User:
    id: int
    username: str
    password: str

users = [
    User(1, 'Admin', '123456'),
    User(2, 'Aasd', '123456'),
    User(3, 'Adminx', '123456'),
]

@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        user = [u for u in users if u.id == session['user_id']][0]
        g.user = user

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # 登录操作
        session.pop('user_id', None)
        username = request.form.get("username", None)
        password = request.form.get("password", None)
        user = [u for u in users if u.username == username]
        if len(user) > 0:
            user = user[0]
        if user and user.password == password:
            session['user_id'] = user.id
            return redirect(url_for('profile'))

    return render_template("login.html")

@app.route('/profile')
def profile():
    if not g.user:
        return redirect(url_for('login'))

    return render_template('profile.html')


if __name__ == '__main__':
    app.run(port=5000, debug=True)
