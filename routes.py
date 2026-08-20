from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from models import db, Record

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def index():
    if current_user.is_admin():
        records = Record.query.order_by(Record.id.desc()).all()
    else:
        records = Record.query.filter_by(user_id=current_user.id).order_by(Record.id.desc()).all()
    return render_template('index.html', records=records, is_admin=current_user.is_admin())

@main_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_record():
    if request.method == 'POST':
        # 获取所有表单字段，顺序与表头一致
        data = {
            'loan_date': request.form['loan_date'],
            'end_date': request.form['end_date'],
            'name': request.form['name'],
            'amount': request.form['amount'],
            'principal': request.form['principal'],
            'weekly': request.form['weekly'],
            'daily': request.form['daily'],
            'profit': request.form['profit'],
            'overdue': request.form['overdue'],
            'receive_time': request.form['receive_time'],
            'remark': request.form['remark'],
            'phone_model': request.form['phone_model'],
            'id_number': request.form['id_number'],
            'imei': request.form['imei'],
            'agent': request.form['agent'],
            'commission': request.form['commission'],
            'supervision': request.form['supervision'],
            'is_android': request.form['is_android'],
        }
        record = Record(user_id=current_user.id, uploader=current_user.username, **data)
        db.session.add(record)
        db.session.commit()
        flash('记录添加成功')
        return redirect(url_for('main.index'))
    return render_template('edit.html', record=None)

@main_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_record(id):
    record = Record.query.get_or_404(id)
    if not current_user.is_admin() and record.user_id != current_user.id:
        abort(403)
    if request.method == 'POST':
        for field in ['loan_date','end_date','name','amount','principal','weekly','daily',
                      'profit','overdue','receive_time','remark','phone_model','id_number',
                      'imei','agent','commission','supervision','is_android']:
            setattr(record, field, request.form[field])
        db.session.commit()
        flash('记录更新成功')
        return redirect(url_for('main.index'))
    return render_template('edit.html', record=record)

@main_bp.route('/delete/<int:id>')
@login_required
def delete_record(id):
    record = Record.query.get_or_404(id)
    if not current_user.is_admin() and record.user_id != current_user.id:
        abort(403)
    db.session.delete(record)
    db.session.commit()
    flash('记录已删除')
    return redirect(url_for('main.index'))
