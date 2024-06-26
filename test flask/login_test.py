from flask import Flask
from dataclasses import dataclass
from flask import render_template, request, url_for, redirect, session, g


app = Flask(__name__, static_url_path="/")
app.config['SECRET_KEY'] = "zx4c6ew1xzc4w65x5cwer4df"

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
