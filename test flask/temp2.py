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


# db = connect()
# cmd = "select * from test3;"
# ret = command(db, cmd)
# print(ret)
delete('hkbin')
# close(db)
