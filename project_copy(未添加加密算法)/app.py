import base64
import time

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from orms import test_deal_info, users, admins, accounts, some_advice
from extensions import register_extension, db
import config, pymysql, requests, json

app = Flask(__name__)
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config.from_object(config)
register_extension(app)
app.secret_key = 'caw465zxc156e4a6w4e5dzxzvc1fdsdad'  # 设置一个密钥，用于 session

id_ = None
salesman_ = None
buyer_ = None
money_ = None
pay_access = False

def get_CA():
    url = "http://43.139.249.124:5000/api"
    headers = {
        "Content-Type": "application/json",
    }
    data = {
        "content": "CA",
        "user": "bank",
    }
    response = requests.post(url, headers=headers, json=data)
    # 输出响应的⽂本内容（可选）
    return response.text


def decry(s_key, data):
    url = "http://43.139.249.124:5000/decode"
    headers = {
        "Content-Type": "application/json",
    }
    data = {
        "key": f"{s_key}",
        "message": f"{data}"
    }
    response = requests.post(url, headers=headers, json=data)
    return response.text


def verify(data, cdata):
    url = "http://43.139.249.124:5000/api"
    headers = {
        "Content-Type": "application/json",
    }
    data = {
        "content": "vertify",
        "user": "dianshang",
        "message": f"{data}",
        "cmessage": f"{cdata}"
    }
    response = requests.post(url, headers=headers, json=data)
    # 输出响应的⽂本内容（可选）
    string = str(response.text)
    json_str = string.replace("'", '"')
    # json.loads() ,要求json串格式中必须的双引号！！转换为字典
    json_dict = json.loads(json_str)
    result = json_dict['details']
    if result == 'True':
        return True
    else:
        return False

def deal(id, salesman, buyer, number):
    # 交易记录加入数据库
    sql_insert_user = "INSERT INTO test_deal_info (id, salesman, buyer, number) VALUES (%s, %s, %s, %s)"
    execute(sql_insert_user, id, salesman, buyer, number)  # 加入数据库
    # 对应加减账户余额
    conn, cursor = get_conn()
    sql = "SELECT money FROM accounts WHERE username = %s"
    cursor.execute(sql, (buyer,))
    result = cursor.fetchone()
    buyer_money = float(result[0])
    if buyer_money < number:
        return False
    else:
        sql = "SELECT money FROM accounts WHERE username = %s"
        cursor.execute(sql, (salesman,))
        result = cursor.fetchone()
        salesman_money = float(result[0])
        buyer_money -= number
        salesman_money += number
        sql = "UPDATE accounts SET money = %s WHERE username = %s"
        execute(sql, round(buyer_money, 2), buyer)
        sql = "UPDATE accounts SET money = %s WHERE username = %s"
        execute(sql, round(salesman_money, 2), salesman)
        close_conn(conn, cursor)
    return

def info_search(database):
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('per_page', type=int, default=10)
    # paginate = test_deal_info.query.paginate(page=page, per_page=per_page, error_out=False)
    q = db.select(database)
    id = request.args.get('id')
    username = request.args.get('username')
    if username and id:
        q = q.where(database.username == username)
        q = q.where(database.id == id)
    if username:
        q = q.where(database.username == username)
    elif id:
        q = q.where(database.id == id)
    paginate = db.paginate(q, page=page, per_page=per_page, error_out=False)
    items: [database] = paginate.items
    return {
        'code': 0,
        'msg': '信息查询成功',
        'count': paginate.total,
        'data': [
            {
                'id': item.id,
                'username': item.username,
                'password': item.password,
            } for item in items
        ]
    }


def feedback_func(username, html):
    if request.method == 'GET':
        if username not in session:
            return redirect(url_for('index'))
        else:
            loggedInUsername = session.get(username)  # 从 session 中获取用户名
            return render_template(html, loggedInUsername=loggedInUsername)

    elif request.method == 'POST':
        username_ = session.get(username)  # 从 session 中获取管理员用户名
        advices = request.form.get('advices')
        # print(advices, username)
        sql_count_id = "SELECT COUNT(*) FROM some_advice"
        count_result = execute(sql_count_id)
        new_id = count_result[0][0] + 1
        sql_insert = "INSERT INTO some_advice (id, username, advice) VALUES (%s, %s, %s)"
        execute(sql_insert, new_id, username_, advices)  # 加入数据库
        return {'code': 0, 'msg': '提交成功'}


def login_func(sql, session_name, url, return_template):
    if request.method == 'POST':
        username = request.form.get('username')  # 接收form表单传参
        password = request.form.get('password')
        res = execute(sql, username, password)
        if res:
            session[session_name] = username  # 将管理员名存储在 session 中
            return redirect(url_for(url, msg='登录成功', loggedInUsername=username))
        else:
            return render_template(return_template, msg='登录失败,用户名或密码错误')
    # get情况
    return render_template(return_template)


def post_data(database):
    data = request.get_json()
    info = database()
    info.update(data)
    try:
        info.save()
    except Exception as e:
        return {
            'code': -1,
            'msg': '新增数据失败'
        }
    return {
        'code': 0,
        'msg': '新增数据成功'
    }


def modify(database, id):
    data = request.get_json()
    # student = StudentORM.query.get(sid)
    info = db.get_or_404(database, id)
    print(info.money)
    info.update(data)
    try:
        info.save()
    except Exception as e:
        return {
            'code': -1,
            'msg': '修改数据失败'
        }
    return {
        'code': 0,
        'msg': '修改数据成功'
    }


def delete(database, id):
    info: database = db.get_or_404(database, id)
    try:
        db.session.delete(info)
        # info.is_del = True
        db.session.commit()
    except Exception as e:
        return {
            'code': -1,
            'msg': '删除数据失败'
        }
    return {
        'code': 0,
        'msg': '删除数据成功'
    }


def get_conn():
    # 建立与mysql连接
    conn = pymysql.connect(host="127.0.0.1", user="root", password="root", db="test", charset="utf8")
    # 创建游标
    cursor = conn.cursor()
    return conn, cursor


def close_conn(conn, cursor):  # 关闭连接
    if cursor:
        cursor.close()
    if conn:
        conn.close()


def execute(sql, *args):  # 执行数据库语句函数
    conn, cursor = get_conn()
    cursor.execute(sql, args)
    res = cursor.fetchall()
    conn.commit()
    close_conn(conn, cursor)
    return res


def get_user_data(username):
    # 连接数据库，执行查询，返回结果
    conn, cursor = get_conn()
    sql = "SELECT username, password FROM users WHERE username = %s"
    cursor.execute(sql, (username,))
    result = cursor.fetchone()
    close_conn(conn, cursor)
    if result:
        username, password = result
        return {'username': username, 'password': password}
    else:
        return None


def newUsername_exists(newUsername, sql):
    # 连接数据库，检查新用户名是否已存在
    # 编写查询数据库的代码，返回 True 或 False
    result = execute(sql, newUsername)
    return bool(result)


def update_user_data(loggedInUsername, newUsername, newPassword):
    # 连接数据库，更新数据库中的用户名和密码
    sql_update = "UPDATE users SET username = %s, password = %s WHERE username = %s"
    execute(sql_update, newUsername, newPassword, loggedInUsername)


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('login.html')


@app.route('/sign_out')
def sign_out():
    session.clear()
    return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    sql = "select id from users where username= %s and password= %s"
    return login_func(sql, 'username', 'user_index', 'login.html')


@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    sql = 'select id from admins where username= %s and password= %s'
    return login_func(sql, 'admin_username', 'admin_index', 'admin_login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == '':
            return render_template('register.html', msg='用户名输入为空，请重试')
        if password == '':
            return render_template('register.html', msg='密码输入为空，请重试')
        # 检查用户名是否已经存在
        sql_check_user = "SELECT id FROM users WHERE username = %s"
        existing_user = execute(sql_check_user, username)
        if existing_user:
            return render_template('register.html', msg='用户名已被占用')
        # 如果用户名没有被占用，则插入新用户数据到数据库中
        sql_count_users = "SELECT COUNT(*) FROM users"
        count_result = execute(sql_count_users)
        new_id = count_result[0][0] + 1
        sql_insert_user = "INSERT INTO users (id, username, password) VALUES (%s, %s, %s)"
        execute(sql_insert_user, new_id, username, password)  # 加入数据库
        return render_template('register.html', msg='注册成功，请登录')
    # get情况
    return render_template('register.html')


@app.route('/user_index')
def user_index():
    if 'username' not in session:
        return redirect(url_for('index'))
    loggedInUsername = session.get('username')  # 从 session 中获取管理员用户名
    return render_template('user_index.html', loggedInUsername=loggedInUsername)


@app.route('/transfer')
def transfer():
    if 'username' not in session:
        return redirect(url_for('index'))
    else:
        loggedInUsername = session.get('username')  # 从 session 中获取管理员用户名
        sql = "SELECT id FROM accounts WHERE username= %s"
        res = execute(sql, loggedInUsername)
        if res:
            return render_template('transfer.html', loggedInUsername=loggedInUsername)
        else:
            return render_template('transfer_none.html', loggedInUsername=loggedInUsername)


@app.route('/transfer_deal', methods=['POST'])
def transfer_deal():
    money = request.form.get('money')
    account_send = request.form.get('account_send')
    account_receive = request.form.get('account_for')
    password = request.form.get('password')
    conn, cursor = get_conn()
    sql = "SELECT pay_pw FROM pay WHERE username = %s"
    cursor.execute(sql, (account_send,))
    result = cursor.fetchone()
    if str(result[0]) == str(password):
        sql = "SELECT money FROM accounts WHERE username = %s"
        cursor.execute(sql, (account_send,))
        result = cursor.fetchone()
        sender_money = float(result[0])
        sql = "SELECT id FROM accounts WHERE username= %s"
        res = execute(sql, account_receive)
        print(res)
        try:
            money = float(money)
            if sender_money < money:
                close_conn(conn, cursor)
                return {'code': 2}  # 余额不足
            if res:
                sql = "SELECT money FROM accounts WHERE username = %s"
                cursor.execute(sql, (account_receive,))
                result = cursor.fetchone()
                receivers_money = float(result[0])
                # 对应加减账户余额
                sender_money -= money
                receivers_money += money
                sql = "UPDATE accounts SET money = %s WHERE username = %s"
                execute(sql, round(sender_money, 2), account_send)
                sql = "UPDATE accounts SET money = %s WHERE username = %s"
                execute(sql, round(receivers_money, 2), account_receive)
                # 写入记录
                sql = "SELECT COUNT(*) FROM test_deal_info"
                count_result = execute(sql)
                id = count_result[0][0] + 1
                sql_insert_user = "INSERT INTO test_deal_info (id, salesman, buyer, number) VALUES (%s, %s, %s, %s)"
                execute(sql_insert_user, id, account_receive, account_send, money)  # 加入数据库
                close_conn(conn, cursor)
                return {'code': 0}  # 成功
            else:
                close_conn(conn, cursor)
                return {'code': 4}  # 成功
        except:
            close_conn(conn, cursor)
            return {'code': 3}   # 其他错误
    else:
        close_conn(conn, cursor)
        return {'code': 1}  # 密码错误


@app.route('/admin_index')
def admin_index():
    if 'admin_username' not in session:
        return redirect(url_for('index'))
    loggedInUsername = session.get('admin_username')  # 从 session 中获取管理员用户名
    return render_template('admin_index.html', loggedInUsername=loggedInUsername)


@app.route('/admin_deal')
def admin_deal():
    if 'admin_username' not in session:
        return redirect(url_for('index'))
    loggedInUsername = session.get('admin_username')  # 从 session 中获取管理员用户名
    return render_template('admin_deal.html', loggedInUsername=loggedInUsername)


@app.route('/users_manage')
def users_manage():
    if 'admin_username' not in session:
        return redirect(url_for('index'))
    loggedInUsername = session.get('admin_username')  # 从 session 中获取管理员用户名
    return render_template('users_manage.html', loggedInUsername=loggedInUsername)


@app.route('/admin_manage')
def admin_manage():
    if 'admin_username' not in session:
        return redirect(url_for('index'))
    loggedInUsername = session.get('admin_username')  # 从 session 中获取管理员用户名
    return render_template('admin_manage.html', loggedInUsername=loggedInUsername)


@app.route('/account')
def account():
    if 'admin_username' not in session:
        return redirect(url_for('index'))
    loggedInUsername = session.get('admin_username')  # 从 session 中获取管理员用户名
    return render_template('account.html', loggedInUsername=loggedInUsername)


@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    return feedback_func('admin_username', 'feedback.html')


@app.route('/feedback_user', methods=['GET', 'POST'])
def feedback_user():
    return feedback_func('username', 'feedback_user.html')


@app.route('/user_manage')
def user_manage():
    if 'username' not in session:
        return redirect(url_for('index'))
    loggedInUsername = session.get('username')
    # 在这里执行数据库查询，获取用户的用户名和密码
    user_data = get_user_data(loggedInUsername)
    if user_data:
        username = user_data['username']
        password = user_data['password']
    else:
        username = ""
        password = ""
    return render_template('user_manage.html', loggedInUsername=loggedInUsername, username=username, password=password)


@app.route('/update_user', methods=['POST'])
def update_user():
    loggedInUsername = request.form.get('loggedInUsername')
    newUsername = request.form.get('newUsername')
    newPassword = request.form.get('newPassword')
    # 检查新用户名是否唯一
    sql = "SELECT id FROM users WHERE username = %s"
    if newUsername_exists(newUsername, sql):
        return {'code': -1, 'msg': '新用户名已存在，请选择其他用户名'}
    if newUsername == '' or newPassword == '':
        return {'code': -1, 'msg': '用户名或密码不可为空'}
    # 更新数据库中的用户名和密码
    update_user_data(loggedInUsername, newUsername, newPassword)
    return {'code': 0, 'msg': '用户信息更新成功'}


@app.route('/user_account')
def user_account():
    if 'username' not in session:
        return redirect(url_for('index'))
    loggedInUsername = session.get('username')
    # 在这里执行数据库查询，获取用户的用户名和密码
    conn, cursor = get_conn()
    username = loggedInUsername
    sql = "SELECT username, money FROM accounts WHERE username = %s"
    cursor.execute(sql, (username,))
    result = cursor.fetchone()
    close_conn(conn, cursor)
    try:
        username, money = result
        if username is None or money is None:
            return render_template('user_account.html')
        user_data = {'username': username, 'money': money}
        if user_data:
            username = user_data['username']
            money = user_data['money']
        else:
            username = ""
            money = ""
        return render_template('user_account.html', loggedInUsername=loggedInUsername, username=username, money=money)
    except:
        return redirect(url_for('user_account_none', loggedInUsername=loggedInUsername))


@app.route('/pay')
def pay():
    if 'username' not in session:
        return redirect(url_for('index'))
    loggedInUsername = session.get('username')
    # 在这里执行数据库查询，获取用户的用户名和密码
    conn, cursor = get_conn()
    sql = "SELECT username, pay_pw FROM pay WHERE username = %s"
    cursor.execute(sql, (loggedInUsername,))
    result = cursor.fetchone()
    close_conn(conn, cursor)
    try:
        username, pay_pw = result
        user_data = {'username': username, 'pay_pw': pay_pw}
        if user_data:
            username = user_data['username']
            pay_pw = user_data['pay_pw']
        else:
            username = ""
            pay_pw = ""
        return render_template('pay.html', loggedInUsername=loggedInUsername, username=username, pay_pw=pay_pw)
    except:
        return redirect(url_for('pay_none', loggedInUsername=loggedInUsername))


@app.route('/pay_none')
def pay_none():
    if 'username' not in session:
        return redirect(url_for('index'))
    loggedInUsername = session.get('username')
    return render_template('pay_none.html', loggedInUsername=loggedInUsername)


@app.route('/user_account_none')
def user_account_none():
    if 'username' not in session:
        return redirect(url_for('index'))
    loggedInUsername = session.get('username')
    return render_template('user_account_none.html', loggedInUsername=loggedInUsername)


@app.route('/update_pay', methods=['POST'])
def update_pay():
    loggedInUsername = request.form.get('loggedInUsername')
    newpay_pw = request.form.get('newpay_pw')
    if len(newpay_pw) != 6 or str.isdigit(newpay_pw) is False:
        return {'code': -1, 'msg': '密码应为数字，不可为空且长度应为6位'}
    # 更新数据库中的支付密码
    sql_update = "UPDATE pay SET pay_pw = %s WHERE username = %s"
    execute(sql_update, newpay_pw, loggedInUsername)
    return {'code': 0, 'msg': '支付密码更改成功'}


@app.route('/user_deal')
def user_deal():
    if 'username' not in session:
        return redirect(url_for('index'))
    loggedInUsername = session.get('username')  # 从 session 中获取管理员用户名
    return render_template('user_deal.html', loggedInUsername=loggedInUsername)


@app.get('/info_add')
def info_add():
    if 'admin_username' not in session:
        return redirect(url_for('index'))
    return render_template('info_add.html')


@app.get('/users_add')
def users_add():
    if 'admin_username' not in session:
        return redirect(url_for('index'))
    return render_template('users_add.html')


@app.get('/admin_add')
def admin_add():
    if 'admin_username' not in session:
        return redirect(url_for('index'))
    return render_template('admin_add.html')


@app.get('/account_add')
def account_add():
    if 'admin_username' not in session:
        return redirect(url_for('index'))
    return render_template('account_add.html')


@app.post('/admin_deal')
def admin_deal_post():
    return post_data(test_deal_info)


@app.post('/users_manage')
def users_manage_post():
    return post_data(users)


@app.post('/admin_manage')
def admin_manage_post():
    return post_data(admins)


@app.post('/account')
def account_post():
    return post_data(accounts)


@app.post('/feedback')
def feedback_post():
    return post_data(some_advice)


# 返回数据+查询服务
@app.route('/info_for_deal')
def info_for_deal():
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('per_page', type=int, default=10)
    # paginate = test_deal_info.query.paginate(page=page, per_page=per_page, error_out=False)
    q = db.select(test_deal_info)
    salesman = request.args.get('salesman')
    id = request.args.get('id')
    if salesman and id:
        q = q.where(test_deal_info.salesman == salesman)
        q = q.where(test_deal_info.id == id)
    if salesman:
        q = q.where(test_deal_info.salesman == salesman)
    elif id:
        q = q.where(test_deal_info.id == id)
    paginate = db.paginate(q, page=page, per_page=per_page, error_out=False)
    items: [test_deal_info] = paginate.items
    if items is None:
        return None
    else:
        return {
            'code': 0,
            'msg': '信息查询成功',
            'count': paginate.total,
            'data': [
                {
                    'id': item.id,
                    'salesman': item.salesman,
                    'buyer': item.buyer,
                    'number': item.number,
                } for item in items
            ]
        }


# 用户查询
@app.route('/info_for_users')
def info_for_users():
    return info_search(users)


@app.route('/info_for_admins')
def info_for_admins():
    return info_search(admins)


# 返回数据+查询服务
@app.route('/info_for_account')
def info_for_account():
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('per_page', type=int, default=10)
    # paginate = test_deal_info.query.paginate(page=page, per_page=per_page, error_out=False)
    q = db.select(accounts)
    username = request.args.get('username')
    id = request.args.get('id')
    if username and id:
        q = q.where(accounts.username == username)
        q = q.where(accounts.id == id)
    if username:
        q = q.where(accounts.username == username)
    elif id:
        q = q.where(accounts.id == id)
    paginate = db.paginate(q, page=page, per_page=per_page, error_out=False)
    items: [accounts] = paginate.items
    return {
        'code': 0,
        'msg': '信息查询成功',
        'count': paginate.total,
        'data': [
            {
                'id': item.id,
                'username': item.username,
                'money': item.money,
            } for item in items
        ]
    }


# 返回数据+查询服务
@app.route('/info_for_user_deal')
def info_for_user_deal():
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('per_page', type=int, default=10)
    # paginate = test_deal_info.query.paginate(page=page, per_page=per_page, error_out=False)
    q = db.select(test_deal_info)
    id = request.args.get('id')
    salesman = request.args.get('salesman')
    loggedInUsername = session.get('username')  # 从 session 中获取管理员用户名
    q = q.where(test_deal_info.buyer == loggedInUsername)
    if salesman and id:
        q = q.where(test_deal_info.salesman == salesman)
        q = q.where(test_deal_info.id == id)
    if salesman:
        q = q.where(test_deal_info.salesman == salesman)
    elif id:
        q = q.where(test_deal_info.id == id)
    paginate = db.paginate(q, page=page, per_page=per_page, error_out=False)
    items: [test_deal_info] = paginate.items
    if items is None:
        return None
    else:
        return {
            'code': 0,
            'msg': '信息查询成功',
            'count': paginate.total,
            'data': [
                {
                    'id': item.id,
                    'salesman': item.salesman,
                    'buyer': item.buyer,
                    'number': item.number,
                } for item in items
            ]
        }


# admin修改交易信息
@app.put('/admin_deal/<int:id>')
def admin_deal_put(id):
    return modify(test_deal_info, id)


# 修改user账号
@app.put('/users_manage/<int:id>')
def users_manage_put(id):
    return modify(users, id)


# admin修改账号
@app.put('/admin_manage/<int:id>')
def admin_manage_put(id):
    return modify(admins, id)


# 修改账户
@app.put('/account/<int:id>')
def account_put(id):
    return modify(accounts, id)


# admin交易删除
@app.delete('/admin_deal/<int:id>')
def admin_deal_del(id):
    return delete(test_deal_info, id)


# admin删除用户账户
@app.delete('/users_manage/<int:id>')
def user_manage_del(id):
    return delete(users, id)


# admin删除admin账户
@app.delete('/admin_manage/<int:id>')
def admin_manage_del(id):
    return delete(admins, id)


# 删除账户
@app.delete('/account/<int:id>')
def account_del(id):
    return delete(accounts, id)


@app.route('/pay_connect', methods=['GET', 'POST'])
def pay_connect():
    if request.method == 'POST':
        global id_, salesman_, buyer_, money_, pay_access
        if id_ is not None:
            pay_pw = request.form.get('pay_pw')
            print(pay_pw)
            sql_check_user = "SELECT pay_pw FROM pay WHERE username = %s"
            result = execute(sql_check_user, buyer_)
            print(result[0][0])
            if str(result[0][0]) == str(pay_pw):
                id = id_
                salesman = salesman_
                buyer = buyer_
                money = money_
                # deal(id, salesman, buyer, money)
                id_ = None
                buyer_ = None
                salesman_ = None  # 清除全局变量，以防止数据泄露
                money_ = None
                pay_access = False
                return render_template('pay-connect.html', msg='支付成功，请返回')
            else:
                return render_template('pay-connect.html', msg='支付失败，密码错误')
        else:
            return redirect(url_for('index'))

    if request.method == 'GET':
        time.sleep(3)
        if pay_access == True:
            return render_template('pay-connect.html')
        else:
            return redirect(url_for('index'))


@app.route('/receive-data', methods=['POST'])
def receive_data():
    data_received = request.get_json()
    # 输出响应的⽂本内容（可选）
    string = str(data_received)
    json_str = string.replace("'", '"')
    # json.loads() ,要求json串格式中必须的双引号！！转换为字典
    json_dict = json.loads(json_str)
    encry_data = json_dict['data']
    verify_data = json_dict['vertify']
    print(encry_data)
    print(verify_data)
    data = decry(s_key, encry_data)
    base64_decode_data = base64.b64decode(data[2:-1])
    message = base64_decode_data.decode()
    print(message)
    if verify(data, verify_data) == True:
        json_str = message.replace("'", '"')
        json_dict = json.loads(json_str)
        id = json_dict['id']
        salesman = json_dict['salesman']
        buyer = json_dict['buyer']
        money = float(json_dict['money'])
        global id_, salesman_, buyer_, money_, pay_access
        id_ = id
        salesman_ = salesman
        buyer_ = buyer
        money_ = money
        pay_access = True
        return jsonify({'message': 'Data received successfully!'})
    else:
        return jsonify({'message': 'Verify fail!'})
    # print(id, salesman, buyer, money)
    # return jsonify({'message': 'Data received successfully!'})


if __name__ == '__main__':
    s_key = get_CA()
    # print(s_key)
    # print(base64.b64decode(s_key))
    app.run(host='0.0.0.0', port=5000)


