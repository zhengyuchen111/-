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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
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


# 添加Jinja2过滤器
@app.template_filter('average')
def average_filter(list_data):
    if not list_data:
        return 0
    return sum(list_data) / len(list_data)


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
             'name': '张三', 'gender': '男', 'class_name': '计算机科学与技术1班', 'student_id': '2025001001'},
            {'username': 'student2', 'email': 'student2@example.com', 'password': '123456',
             'name': '李四', 'gender': '女', 'class_name': '计算机科学与技术1班', 'student_id': '2025001002'},
            {'username': 'student3', 'email': 'student3@example.com', 'password': '123456',
             'name': '王五', 'gender': '男', 'class_name': '软件工程1班', 'student_id': '2025002001'},
            {'username': 'student4', 'email': 'student4@example.com', 'password': '123456',
             'name': '赵六', 'gender': '女', 'class_name': '人工智能1班', 'student_id': '2025003001'},
            {'username': 'student5', 'email': 'student5@example.com', 'password': '123456',
             'name': '钱七', 'gender': '男', 'class_name': '信息安全1班', 'student_id': '2025004001'}
        ]

        courses_list = Course.query.all()

        for data in students_data:
            existing_user = User.query.filter_by(username=data['username']).first()
            if not existing_user:
                user = User(
                    username=data['username'],
                    email=data['email'],
                    password=data['password']
                )
                db.session.add(user)
                db.session.flush()

                existing_student = Student.query.filter_by(student_id=data['student_id']).first()
                if not existing_student:
                    student = Student(
                        student_id=data['student_id'],
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
            return redirect(url_for('user_grades'))

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
        # 获取表单数据
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # 表单验证
        if not username or not email or not password or not confirm_password:
            flash('所有字段都是必填项！', 'error')
            return render_template('register.html', username=username, email=email)

        if password != confirm_password:
            flash('两次输入的密码不一致！', 'error')
            return render_template('register.html', username=username, email=email)

        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            flash('用户名已被注册，请选择其他用户名！', 'error')
            return render_template('register.html', email=email)

        # 检查邮箱是否已存在
        if User.query.filter_by(email=email).first():
            flash('该邮箱已被注册，请使用其他邮箱！', 'error')
            return render_template('register.html', username=username)

        # 创建新用户
        try:
            new_user = User(
                username=username,
                email=email,
                password=password,  # 注意：实际项目中应该加密存储密码
                is_active=True
            )
            db.session.add(new_user)
            db.session.commit()

            # 注册成功，跳转到登录页
            flash('注册成功！请使用您的账号登录。', 'success')
            return redirect(url_for('login'))

        except Exception as e:
            db.session.rollback()
            flash(f'注册失败：{str(e)}', 'error')
            return render_template('register.html', username=username, email=email)

    # GET请求，显示注册表单
    return render_template('register.html')


@app.route('/user/profile', methods=['GET', 'POST'])
@login_required
def user_profile():
    user = db.session.get(User, session['user_id'])  # 使用新的get方法
    student = user.student
    classes = SchoolClass.query.all()

    if request.method == 'POST':
        user.email = request.form.get('email')
        if request.form.get('password'):
            user.password = request.form.get('password')

        student_id = request.form.get('student_id')

        existing_student = Student.query.filter_by(student_id=student_id).first()
        if existing_student and existing_student.user_id != user.id:
            flash(f'学号 {student_id} 已被其他账户绑定！', 'error')
            return render_template('user/profile.html', user=user, student=student, classes=classes)

        if student:
            student.name = request.form.get('name')
            student.gender = request.form.get('gender')
            student.class_name = request.form.get('class_name')
            if request.form.get('birth_date'):
                student.birth_date = datetime.strptime(request.form.get('birth_date'), '%Y-%m-%d').date()
        else:
            new_student = Student(
                student_id=student_id,
                name=request.form.get('name'),
                gender=request.form.get('gender'),
                class_name=request.form.get('class_name'),
                birth_date=datetime.strptime(request.form.get('birth_date'), '%Y-%m-%d').date() if request.form.get(
                    'birth_date') else None,
                user_id=user.id
            )
            db.session.add(new_student)

        try:
            db.session.commit()
            flash('个人信息更新成功！', 'success')
            return redirect(url_for('user_grades'))
        except Exception as e:
            db.session.rollback()
            flash(f'绑定失败：{str(e)}', 'error')

    return render_template('user/profile.html', user=user, student=student, classes=classes)


@app.route('/user/grades')
@login_required
def user_grades():
    user = db.session.get(User, session['user_id'])  # 使用新的get方法
    student = user.student
    grades = []
    courses = Course.query.all()

    if student:
        grades = Grade.query.join(Course).filter(Grade.student_id == student.id).all()

    return render_template('user/grades.html', user=user, student=student, grades=grades, courses=courses)


@app.route('/user/courses')  # 确保这个路由存在
@login_required
def user_courses():
    user = db.session.get(User, session['user_id'])  # 使用新的get方法
    student = user.student
    courses = Course.query.all()
    selected_courses = []
    grades = []

    if student:
        grades = Grade.query.filter_by(student_id=student.id).all()
        selected_courses = [grade.course_id for grade in grades]

    return render_template('user/courses.html', user=user, student=student,
                           courses=courses, selected_courses=selected_courses, grades=grades)


@app.route('/logout')
def logout():
    session.clear()
    flash('已成功退出登录', 'success')
    return redirect(url_for('login'))


# 管理员路由
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


# 在admin_required装饰器之后添加以下路由
@app.route('/admin/students/add', methods=['POST'])
@admin_required
def admin_add_student():
    student_id = request.form.get('student_id')
    name = request.form.get('name')
    gender = request.form.get('gender')
    class_name = request.form.get('class_name')

    # 检查学号是否已存在
    existing_student = Student.query.filter_by(student_id=student_id).first()
    if existing_student:
        flash('学号已存在！', 'error')
        return redirect(url_for('admin_students'))

    # 创建用户账号（默认密码123456）
    username = f"student_{student_id[-4:]}"
    email = f"{student_id}@school.com"

    # 确保用户名唯一
    if User.query.filter_by(username=username).first():
        username = f"student_{student_id}"

    # 创建用户和学生记录
    new_user = User(
        username=username,
        email=email,
        password='123456'  # 默认密码
    )
    db.session.add(new_user)
    db.session.flush()  # 获取user.id但不提交

    new_student = Student(
        student_id=student_id,
        name=name,
        gender=gender,
        class_name=class_name,
        user_id=new_user.id
    )
    db.session.add(new_student)
    db.session.commit()

    flash(f'学生添加成功！账号：{username}，默认密码：123456', 'success')
    return redirect(url_for('admin_students'))


# 同时添加编辑和删除学生的路由
@app.route('/admin/students/edit/<int:student_id>', methods=['POST'])
@admin_required
def admin_edit_student(student_id):
    student = Student.query.get_or_404(student_id)
    student.name = request.form.get('name')
    student.gender = request.form.get('gender')
    student.class_name = request.form.get('class_name')

    if request.form.get('birth_date'):
        student.birth_date = datetime.strptime(request.form.get('birth_date'), '%Y-%m-%d').date()

    db.session.commit()
    flash('学生信息更新成功！', 'success')
    return redirect(url_for('admin_students'))


@app.route('/admin/students/delete/<int:student_id>', methods=['POST'])
@admin_required
def admin_delete_student(student_id):
    student = Student.query.get_or_404(student_id)

    # 删除关联的用户账号
    if student.user:
        db.session.delete(student.user)

    db.session.delete(student)
    db.session.commit()
    flash('学生信息已删除！', 'success')
    return redirect(url_for('admin_students'))


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


# 课程管理路由
@app.route('/admin/courses/add', methods=['POST'])
@admin_required
def admin_add_course():
    course_code = request.form.get('course_code')
    course_name = request.form.get('course_name')
    credit = float(request.form.get('credit'))
    semester = request.form.get('semester')

    existing_course = Course.query.filter_by(course_code=course_code).first()
    if existing_course:
        flash('课程代码已存在！', 'error')
        return redirect(url_for('admin_courses'))

    new_course = Course(
        course_code=course_code,
        course_name=course_name,
        credit=credit,
        semester=semester
    )
    db.session.add(new_course)
    db.session.commit()
    flash('课程添加成功！', 'success')
    return redirect(url_for('admin_courses'))


@app.route('/admin/courses/edit/<int:course_id>', methods=['POST'])
@admin_required
def admin_edit_course(course_id):
    course = Course.query.get_or_404(course_id)
    course.course_name = request.form.get('course_name')
    course.credit = float(request.form.get('credit'))
    course.semester = request.form.get('semester')

    db.session.commit()
    flash('课程更新成功！', 'success')
    return redirect(url_for('admin_courses'))


@app.route('/admin/courses/delete/<int:course_id>', methods=['POST'])
@admin_required
def admin_delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    flash('课程已删除！', 'success')
    return redirect(url_for('admin_courses'))


# 管理员成绩管理页面
@app.route('/admin/grades')
@admin_required
def admin_grades():
    page = request.args.get('page', 1, type=int)

    # 获取所有成绩（关联学生和课程信息）
    grades = Grade.query.join(Student).join(Course).order_by(
        Student.class_name, Student.name, Course.course_name
    ).paginate(page=page, per_page=15)

    # 获取所有学生和课程用于添加成绩
    students = Student.query.order_by(Student.class_name, Student.name).all()
    courses = Course.query.order_by(Course.course_code).all()

    return render_template('admin/grades.html',
                           grades=grades,
                           students=students,
                           courses=courses)


# 添加/更新成绩
@app.route('/admin/grades/add', methods=['POST'])
@admin_required
def admin_add_grade():
    student_id = request.form.get('student_id')
    course_id = request.form.get('course_id')
    score = float(request.form.get('score'))

    # 检查是否已有该学生的该课程成绩
    existing_grade = Grade.query.filter_by(
        student_id=student_id,
        course_id=course_id
    ).first()

    if existing_grade:
        # 更新现有成绩
        existing_grade.score = score
        existing_grade.grade_level = calculate_grade_level(score)
        flash('成绩已更新！', 'success')
    else:
        # 添加新成绩
        new_grade = Grade(
            student_id=student_id,
            course_id=course_id,
            score=score,
            grade_level=calculate_grade_level(score),
            exam_date=datetime.now().date()
        )
        db.session.add(new_grade)
        flash('成绩添加成功！', 'success')

    db.session.commit()
    return redirect(url_for('admin_grades'))


# 编辑成绩
@app.route('/admin/grades/edit/<int:grade_id>', methods=['POST'])
@admin_required
def admin_edit_grade(grade_id):
    grade = Grade.query.get_or_404(grade_id)
    score = float(request.form.get('score'))

    # 更新成绩和等级
    grade.score = score
    grade.grade_level = calculate_grade_level(score)
    db.session.commit()

    flash('成绩修改成功！', 'success')
    return redirect(url_for('admin_grades'))


# 删除成绩
@app.route('/admin/grades/delete/<int:grade_id>', methods=['POST'])
@admin_required
def admin_delete_grade(grade_id):
    grade = Grade.query.get_or_404(grade_id)
    db.session.delete(grade)
    db.session.commit()

    flash('成绩已删除！', 'success')
    return redirect(url_for('admin_grades'))


if __name__ == '__main__':
    app.run(debug=True)