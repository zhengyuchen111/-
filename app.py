from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
import random
import string

app = Flask(__name__)
app.secret_key = 'score_system_key_2025'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# 数据库模型定义
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    is_active = db.Column(db.Boolean, default=True)
    student = db.relationship('Student', backref='user', uselist=False, lazy=True)


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    is_super = db.Column(db.Boolean, default=False)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(10))
    birth_date = db.Column(db.Date)
    class_name = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    grades = db.relationship('Grade', backref='student', lazy=True, cascade="all, delete-orphan")


class SchoolClass(db.Model):
    __tablename__ = 'classes'
    id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(50), unique=True, nullable=False)
    major = db.Column(db.String(50))
    grade = db.Column(db.String(20))


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(20), unique=True, nullable=False)
    course_name = db.Column(db.String(100), nullable=False)
    credit = db.Column(db.Float, default=1.0)
    semester = db.Column(db.String(20))
    grades = db.relationship('Grade', backref='course', lazy=True)


class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)
    grade_level = db.Column(db.String(10))
    exam_date = db.Column(db.Date, default=datetime.now)
    __table_args__ = (db.UniqueConstraint('student_id', 'course_id', name='unique_student_course'),)


# 辅助函数
def calculate_grade_level(score):
    if score >= 90:
        return '优'
    elif score >= 80:
        return '良'
    elif score >= 70:
        return '中'
    elif score >= 60:
        return '及格'
    else:
        return '不及格'


def generate_student_id():
    return '2025' + ''.join(random.choices(string.digits, k=6))


# 装饰器
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session or datetime.now().timestamp() >= session.get('expires_at', 0):
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session or session.get('role') != 'admin':
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)

    return decorated


# 初始化数据库和测试数据
with app.app_context():
    db.create_all()

    if not Admin.query.filter_by(username='admin').first():
        admin = Admin(username='admin', email='admin@example.com', password='admin123', is_super=True)
        db.session.add(admin)

    if not SchoolClass.query.first():
        classes = [
            SchoolClass(class_name='计算机科学与技术1班', major='计算机科学与技术', grade='2025级'),
            SchoolClass(class_name='计算机科学与技术2班', major='计算机科学与技术', grade='2025级'),
            SchoolClass(class_name='软件工程1班', major='软件工程', grade='2025级'),
            SchoolClass(class_name='人工智能1班', major='人工智能', grade='2025级'),
            SchoolClass(class_name='信息安全1班', major='信息安全', grade='2025级')
        ]
        db.session.add_all(classes)

    if not Course.query.first():
        courses = [
            Course(course_code='MATH101', course_name='高等数学', credit=4.0, semester='2025-1'),
            Course(course_code='ENG101', course_name='大学英语', credit=3.0, semester='2025-1'),
            Course(course_code='PHY101', course_name='大学物理', credit=3.5, semester='2025-1'),
            Course(course_code='PROG101', course_name='程序设计基础', credit=3.0, semester='2025-1'),
            Course(course_code='POL101', course_name='思想政治', credit=2.0, semester='2025-1'),
            Course(course_code='DS101', course_name='数据结构', credit=3.5, semester='2025-2'),
            Course(course_code='OS101', course_name='操作系统', credit=3.0, semester='2025-2')
        ]
        db.session.add_all(courses)

    if User.query.count() <= 1:
        students_data = [
            {'username': 'student1', 'email': 'student1@example.com', 'password': '123456',
             'name': '张三', 'gender': '男', 'class_name': '计算机科学与技术1班'},
            {'username': 'student2', 'email': 'student2@example.com', 'password': '123456',
             'name': '李四', 'gender': '女', 'class_name': '计算机科学与技术1班'},
            {'username': 'student3', 'email': 'student3@example.com', 'password': '123456',
             'name': '王五', 'gender': '男', 'class_name': '软件工程1班'},
            {'username': 'student4', 'email': 'student4@example.com', 'password': '123456',
             'name': '赵六', 'gender': '女', 'class_name': '人工智能1班'},
            {'username': 'student5', 'email': 'student5@example.com', 'password': '123456',
             'name': '钱七', 'gender': '男', 'class_name': '信息安全1班'}
        ]

        courses_list = Course.query.all()

        for data in students_data:
            user = User(
                username=data['username'],
                email=data['email'],
                password=data['password']
            )
            db.session.add(user)
            db.session.flush()

            student = Student(
                student_id=generate_student_id(),
                name=data['name'],
                gender=data['gender'],
                class_name=data['class_name'],
                user_id=user.id
            )
            db.session.add(student)
            db.session.flush()

            for course in random.sample(courses_list, 4):
                score = round(random.uniform(60, 98), 1)
                grade = Grade(
                    student_id=student.id,
                    course_id=course.id,
                    score=score,
                    grade_level=calculate_grade_level(score)
                )
                db.session.add(grade)

    db.session.commit()


# 路由定义
@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username, password=password).first()
        if not user and '@' in username:
            user = User.query.filter_by(email=username, password=password).first()

        if user and user.is_active:
            session['username'] = user.username
            session['role'] = 'user'
            session['user_id'] = user.id
            session['expires_at'] = (datetime.now() + timedelta(hours=2)).timestamp()
            return redirect(url_for('user_profile'))  # 登录后直接进入个人信息页面

        flash('用户名/密码错误或账号已禁用', 'error')

    return render_template('login.html')


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        admin = Admin.query.filter_by(username=username, password=password).first()
        if admin:
            session['username'] = admin.username
            session['role'] = 'admin'
            session['user_id'] = admin.id
            session['expires_at'] = (datetime.now() + timedelta(hours=2)).timestamp()
            return redirect(url_for('admin_students'))

        flash('管理员账号或密码错误', 'error')

    return render_template('admin_login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('两次密码不一致', 'error')
            return render_template('register.html', username=username, email=email)

        if User.query.filter_by(username=username).first():
            flash('用户名已存在', 'error')
            return render_template('register.html', email=email)

        if User.query.filter_by(email=email).first():
            flash('邮箱已被注册', 'error')
            return render_template('register.html', username=username)

        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('注册成功，请登录', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


# 用户功能 - 移除仪表盘，优化导航
@app.route('/user/profile', methods=['GET', 'POST'])
@login_required
def user_profile():
    user = User.query.get(session['user_id'])
    student = user.student
    classes = SchoolClass.query.all()  # 获取所有班级供选择

    if request.method == 'POST':
        # 更新用户信息
        user.email = request.form.get('email')
        if request.form.get('password'):
            user.password = request.form.get('password')

        # 更新或创建学生信息
        if student:
            student.name = request.form.get('name')
            student.gender = request.form.get('gender')
            student.student_id = request.form.get('student_id')
            student.class_name = request.form.get('class_name')
            if request.form.get('birth_date'):
                student.birth_date = datetime.strptime(request.form.get('birth_date'), '%Y-%m-%d').date()
        else:
            # 创建新的学生记录关联到当前用户
            new_student = Student(
                student_id=request.form.get('student_id'),
                name=request.form.get('name'),
                gender=request.form.get('gender'),
                class_name=request.form.get('class_name'),
                birth_date=datetime.strptime(request.form.get('birth_date'), '%Y-%m-%d').date() if request.form.get(
                    'birth_date') else None,
                user_id=user.id
            )
            db.session.add(new_student)

        db.session.commit()
        flash('个人信息更新成功！', 'success')
        return redirect(url_for('user_grades'))  # 更新后跳转到成绩页面

    return render_template('user/profile.html', user=user, student=student, classes=classes)


@app.route('/user/grades')
@login_required
def user_grades():
    user = User.query.get(session['user_id'])
    student = user.student
    grades = []
    courses = Course.query.all()

    if student:
        grades = Grade.query.join(Course).filter(Grade.student_id == student.id).all()

    return render_template('user/grades.html', user=user, student=student, grades=grades, courses=courses)


@app.route('/user/grades/add', methods=['POST'])
@login_required
def add_grade():
    user = User.query.get(session['user_id'])
    student = user.student

    if not student:
        flash('请先完善个人信息', 'error')
        return redirect(url_for('user_profile'))

    course_id = request.form.get('course_id')
    score = float(request.form.get('score'))

    # 检查是否已存在该课程成绩
    existing_grade = Grade.query.filter_by(student_id=student.id, course_id=course_id).first()
    if existing_grade:
        existing_grade.score = score
        existing_grade.grade_level = calculate_grade_level(score)
    else:
        new_grade = Grade(
            student_id=student.id,
            course_id=course_id,
            score=score,
            grade_level=calculate_grade_level(score)
        )
        db.session.add(new_grade)

    db.session.commit()
    flash('成绩添加/更新成功！', 'success')
    return redirect(url_for('user_grades'))


@app.route('/user/grades/delete/<int:grade_id>', methods=['POST'])
@login_required
def delete_grade(grade_id):
    grade = Grade.query.get_or_404(grade_id)
    user = User.query.get(session['user_id'])

    if grade.student.user_id != user.id:
        flash('无权删除该成绩', 'error')
        return redirect(url_for('user_grades'))

    db.session.delete(grade)
    db.session.commit()
    flash('成绩已删除', 'success')
    return redirect(url_for('user_grades'))


@app.route('/user/courses')
@login_required
def user_courses():
    user = User.query.get(session['user_id'])
    student = user.student
    courses = Course.query.all()

    # 获取该学生已选课程
    selected_courses = []
    if student:
        selected_grades = Grade.query.filter_by(student_id=student.id).all()
        selected_courses = [grade.course_id for grade in selected_grades]

    return render_template('user/courses.html', user=user, student=student,
                           courses=courses, selected_courses=selected_courses)


@app.route('/logout')
def logout():
    session.clear()
    flash('已成功退出登录', 'success')
    return redirect(url_for('login'))


# 管理员功能保持不变
@app.route('/admin/students')
@admin_required
def admin_students():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')

    query = Student.query.join(User)
    if search:
        query = query.filter(
            db.or_(
                Student.name.contains(search),
                Student.student_id.contains(search),
                User.username.contains(search)
            )
        )

    students = query.order_by(Student.class_name, Student.name).paginate(page=page, per_page=10)

    return render_template('admin/students.html', students=students, search=search)


@app.route('/admin/student/<int:student_id>')
@admin_required
def admin_student_detail(student_id):
    student = Student.query.get_or_404(student_id)
    grades = Grade.query.join(Course).filter(Grade.student_id == student.id).all()

    return render_template('admin/student_detail.html', student=student, grades=grades)


@app.route('/admin/courses')
@admin_required
def admin_courses():
    courses = Course.query.all()
    return render_template('admin/courses.html', courses=courses)


@app.route('/admin/grades')
@admin_required
def admin_grades():
    page = request.args.get('page', 1, type=int)
    grades = Grade.query.join(Student).join(Course).order_by(Student.name, Course.course_name).paginate(page=page,
                                                                                                        per_page=15)

    return render_template('admin/grades.html', grades=grades)


if __name__ == '__main__':
    app.run(debug=True)