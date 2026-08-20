from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='user')   # admin / user
    records = db.relationship('Record', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # 新表头字段（去掉了“手机号”，增加了“下款日期”和“结束日期”）
    loan_date = db.Column(db.String(20))          # 下款日期
    end_date = db.Column(db.String(20))           # 结束日期
    name = db.Column(db.String(50))               # 姓名
    amount = db.Column(db.String(20))             # 额度
    principal = db.Column(db.String(20))          # 本金
    weekly = db.Column(db.String(20))             # 周续
    daily = db.Column(db.String(20))              # 天续
    profit = db.Column(db.String(20))             # 利润
    overdue = db.Column(db.String(20))            # 逾期
    receive_time = db.Column(db.String(50))       # 收款时间
    remark = db.Column(db.String(200))            # 备注
    phone_model = db.Column(db.String(30))        # 手机型号（原手机编号）
    id_number = db.Column(db.String(30))          # 身份证号码
    imei = db.Column(db.String(30))               # IMEI
    agent = db.Column(db.String(50))              # 中介
    commission = db.Column(db.String(20))         # 佣金
    supervision = db.Column(db.String(20))        # 监管期
    is_android = db.Column(db.String(10))         # 是否安卓

    # 冗余字段：上传者用户名
    uploader = db.Column(db.String(80))

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
