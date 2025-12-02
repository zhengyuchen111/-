from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime, timedelta
import re

app = Flask(__name__)
app.secret_key = 'score_system_key'

# 使用字典存储数据（替代数据库）
# 用户数据
users = {
    'zhangsan': {'password': '123', 'email': 'zhangsan@example.com', 'id': 1},
    'lisi': {'password': '456', 'email': 'lisi@example.com', 'id': 2},
    'wangwu': {'password': '789', 'email': 'wangwu@example.com', 'id': 3},
    'zhaoliu': {'password': '000', 'email': 'zhaoliu@example.com', 'id': 4},
    'qianqi': {'password': '111', 'email': 'qianqi@example.com', 'id': 5}
}

# 管理员数据
admins = {
    'admin': {'password': 'admin123', 'id': 1}
}

# 成绩数据
scores = {
    # 张三的成绩
    1: [
        {'subject': '数学', 'grade': 95},
        {'subject': '语文', 'grade': 88},
        {'subject': '英语', 'grade': 92}
    ],
    # 李四的成绩
    2: [
        {'subject': '数学', 'grade': 82},
        {'subject': '语文', 'grade': 90},
        {'subject': '英语', 'grade': 76}
    ],
    # 王五的成绩
    3: [
        {'subject': '数学', 'grade': 78},
        {'subject': '语文', 'grade': 85},
        {'subject': '英语', 'grade': 90}
    ],
    # 赵六的成绩
    4: [
        {'subject': '数学', 'grade': 92},
        {'subject': '语文', 'grade': 80},
        {'subject': '英语', 'grade': 88}
    ],
    # 钱七的成绩
    5: [
        {'subject': '数学', 'grade': 85},
        {'subject': '语文', 'grade': 93},
        {'subject': '英语', 'grade': 79}
    ]
}


# 计算所有学生的总成绩和排名
def get_ranking_data():
    total_scores = {}

    for username, user_data in users.items():
        user_id = user_data['id']
        if user_id in scores:
            total = sum(score['grade'] for score in scores[user_id])
            total_scores[username] = total

    # 按总分降序排序
    sorted_ranking = sorted(total_scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_ranking


# 获取用户ID
def get_user_id(username):
    if username in users:
        return users[username]['id']
    return None


# 验证用户登录（支持用户名或邮箱）
def authenticate_user(login_id, password):
    # 检查是否是邮箱登录
    if '@' in login_id:
        for username, user_data in users.items():
            if user_data.get('email') == login_id and user_data['password'] == password:
                return username
        return None
    # 用户名登录
    elif login_id in users and users[login_id]['password'] == password:
        return login_id
    return None


# 验证管理员登录
def authenticate_admin(username, password):
    return username in admins and admins[username]['password'] == password


# 获取用户成绩
def get_user_scores(username):
    user_id = get_user_id(username)
    if user_id and user_id in scores:
        return scores[user_id]
    return []


# 视图函数：home
@app.route('/')
def home():
    if 'username' in session and datetime.now().timestamp() < session.get('expires_at', 0):
        return redirect(url_for('score'))
    return redirect(url_for('login'))


# 视图函数：login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        login_type = request.form.get('login_type', 'user')

        # 管理员登录验证
        if login_type == 'admin':
            if authenticate_admin(username, password):
                session['username'] = username
                session['role'] = 'admin'
                session['expires_at'] = (datetime.now() + timedelta(minutes=30)).timestamp()
                return redirect(url_for('admin_dashboard'))
            return render_template('login.html', error='管理员账号或密码错误',
                                   username=username)

        # 用户登录验证（支持用户名或邮箱）
        authenticated_user = authenticate_user(username, password)
        if authenticated_user:
            session['username'] = authenticated_user
            session['role'] = 'user'
            session['expires_at'] = (datetime.now() + timedelta(minutes=30)).timestamp()
            return redirect(url_for('score'))

        # 友好的错误提示
        error_msg = '用户名/邮箱或密码错误，请重试'
        return render_template('login.html', error=error_msg, username=username)

    return render_template('login.html')


# 注册功能
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # 表单验证
        errors = {}

        # 用户名验证
        if not username or len(username) < 3:
            errors['username_error'] = '用户名至少需要3个字符'
        elif username in users:
            errors['username_error'] = '用户名已存在'

        # 邮箱验证
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not email or not re.match(email_pattern, email):
            errors['email_error'] = '请输入有效的邮箱地址'
        else:
            # 检查邮箱是否已存在
            for user_data in users.values():
                if user_data.get('email') == email:
                    errors['email_error'] = '邮箱已被注册'
                    break

        # 密码验证
        if not password or len(password) < 6:
            errors['password_error'] = '密码至少需要6个字符'

        # 确认密码验证
        if password != confirm_password:
            errors['confirm_error'] = '两次输入的密码不一致'

        # 如果有错误，返回表单并显示错误信息
        if errors:
            return render_template('register.html', **errors,
                                   username=username, email=email)

        # 创建新用户（内存中）
        new_user_id = max([user['id'] for user in users.values()]) + 1 if users else 1
        users[username] = {
            'password': password,
            'email': email,
            'id': new_user_id
        }

        # 为新用户创建空成绩记录
        scores[new_user_id] = []

        return render_template('register.html', success='注册成功！请登录')

    return render_template('register.html')


# 管理员面板
@app.route('/admin')
def admin_dashboard():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('login', type='admin'))

    return render_template('admin.html', users=users)


@app.route('/score')
def score():
    if 'username' not in session or datetime.now().timestamp() >= session.get('expires_at', 0):
        return redirect(url_for('login'))

    username = session['username']
    # 获取当前用户的成绩
    user_scores = get_user_scores(username)
    user_scores_list = [(score['subject'], score['grade']) for score in user_scores]
    user_total = sum(grade for _, grade in user_scores_list)
    ranking_data = get_ranking_data()  # 获取排名数据

    # 获取当前用户的排名
    current_rank = [i + 1 for i, (user, _) in enumerate(ranking_data) if user == username][0]

    # 处理排名数据，添加索引
    ranking_with_index = [(i + 1, user, total) for i, (user, total) in enumerate(ranking_data)]

    return render_template('score.html',
                           username=username,
                           scores=user_scores_list,
                           user_total=user_total,
                           ranking_data=ranking_with_index,  # 传递处理后的数据
                           current_rank=current_rank)


# 视图函数：logoff
@app.route('/logoff')
def logoff():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=False)