import os
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-me')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ---------- 模型 ----------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    records = db.relationship('Record', backref='uploader', lazy=True)

class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    loan_date = db.Column(db.String(20), nullable=False)
    end_date = db.Column(db.String(20), nullable=True)
    name = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    principal = db.Column(db.Float, nullable=False)
    weekly = db.Column(db.Float, nullable=True)
    daily = db.Column(db.Float, nullable=True)
    profit = db.Column(db.Float, nullable=True)
    overdue = db.Column(db.String(20), nullable=True)
    receive_time = db.Column(db.String(50), nullable=True)
    remark = db.Column(db.String(200), nullable=True)
    phone_model = db.Column(db.String(50), nullable=True)
    id_card = db.Column(db.String(30), nullable=True)
    imei = db.Column(db.String(50), nullable=True)
    agent = db.Column(db.String(50), nullable=True)
    commission = db.Column(db.Float, nullable=True)
    supervision_period = db.Column(db.String(50), nullable=True)
    is_android = db.Column(db.String(10), nullable=True)
    uploader_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def init_db():
    with app.app_context():
        db.create_all()
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', password=generate_password_hash('admin123'), is_admin=True)
            db.session.add(admin)
            db.session.commit()

# ---------- 路由 ----------
@app.route('/')
@login_required
def index():
    if current_user.is_admin:
        records = Record.query.order_by(Record.created_at.desc()).all()
    else:
        records = Record.query.filter_by(uploader_id=current_user.id).order_by(Record.created_at.desc()).all()
    return render_template('index.html', records=records)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        try:
            record = Record(
                loan_date=request.form['loan_date'],
                end_date=request.form.get('end_date'),
                name=request.form['name'],
                amount=float(request.form['amount']),
                principal=float(request.form['principal']),
                weekly=float(request.form['weekly']) if request.form.get('weekly') else None,
                daily=float(request.form['daily']) if request.form.get('daily') else None,
                profit=float(request.form['profit']) if request.form.get('profit') else None,
                overdue=request.form.get('overdue'),
                receive_time=request.form.get('receive_time'),
                remark=request.form.get('remark'),
                phone_model=request.form.get('phone_model'),
                id_card=request.form.get('id_card'),
                imei=request.form.get('imei'),
                agent=request.form.get('agent'),
                commission=float(request.form['commission']) if request.form.get('commission') else None,
                supervision_period=request.form.get('supervision_period'),
                is_android=request.form.get('is_android'),
                uploader_id=current_user.id
            )
            db.session.add(record)
            db.session.commit()
            flash('✅ 数据上传成功！', 'success')
        except Exception as e:
            flash(f'❌ 上传失败: {e}', 'danger')
        return redirect(url_for('index'))
    return render_template('upload.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        flash('❌ 用户名或密码错误', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('⚠️ 用户名已存在', 'warning')
        else:
            hashed = generate_password_hash(password)
            user = User(username=username, password=hashed)
            db.session.add(user)
            db.session.commit()
            flash('✅ 注册成功，请登录', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
