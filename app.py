from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import base64
import os
from datetime import datetime
from werkzeug.utils import secure_filename


from models import User, Employee, Doc
from manage_db import default_admin
from db import SessionLocal, Base

db = SessionLocal()

app = Flask(__name__)

app.secret_key = "my_secret_key"
# create default user
default_admin()
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def user_loader(user_id):
    return db.query(User).get(int(user_id))

# views

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=["POST","GET"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":

        email = request.form['email']
        password = request.form['password']

        user = db.query(User).filter_by(email=email,password=password).first()
        if user:
            login_user(user)
            return redirect('/action')
        else:
            flash('Incorrect user name or password')
            return render_template('login.html')

# auth

@app.route('/action')
@login_required
def action():
    employees = db.query(Employee).all()
    print(employees)
    return render_template('action.html', employees=employees)

@app.route('/employee/<int:id>')
@login_required
def employee_detail(id):
    employee = db.query(Employee).get(id)
    doc = db.query(Doc).filter_by(employee_id=id).all()
    if not employee:
        flash("Employee not found")
        return redirect('/action')
    return render_template('employee_detail.html', employee=employee, doc=doc)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")

# api(auth)

@app.route('/api/employ', methods=['POST'])
@login_required
def employ_add():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    # Check duplicate fanID
    existing = db.query(Employee).filter_by(fanID=data.get('fanID')).first()
    if existing:
        return jsonify({"error": "Employee with this Fan ID already exists"}), 400

    def parse_date(date_str):
        if date_str:
            try:
                return datetime.strptime(date_str, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                return None
        return None

    # Handle Base64 photo
    photo_base64 = data.get('photo')
    fan_id = data.get('fanID', 'unknown')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    # Create Employee – note join_year is converted to date
    employee = Employee(
        fname=data.get('fname'),
        mname=data.get('mname'),
        lname=data.get('lname'),
        gender=data.get('gender'),
        fanID=data.get('fanID'),
        birthdate=parse_date(data.get('birthdate')),
        phone_number=data.get('phone_number'),
        edu_level=data.get('edu_level'),
        profession=data.get('profession'),
        work_experience=data.get('work_experience'),
        group_name=data.get('group_name'),
        position_in_group=data.get('position_in_group'),
        join_year=parse_date(data.get('join_year')),
        work_place=data.get('work_place'),
        work_place_name=data.get('work_place_name'),
        salary=data.get('salary'),
        werada=data.get('werada'),
        kebele=data.get('kebele'),
        house_number=data.get('house_number'),
        photo_url=f"profile_pics/{fan_id}_{timestamp}.jpg"
    )

    db.add(employee)
    try:
        if photo_base64 and photo_base64 != 'null':
            if ',' in photo_base64:
                photo_base64 = photo_base64.split(',')[1]
            try:
                photo_data = base64.b64decode(photo_base64)
                fan_id = data.get('fanID', 'unknown')
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                photo_filename = f"{fan_id}_{timestamp}.jpg"
                os.makedirs('static/profile_pics', exist_ok=True)
                with open(f"static/profile_pics/{photo_filename}", 'wb') as f:
                    f.write(photo_data)
            except Exception as e:
                return jsonify({"error": "Failed to save photo"}), 500
            db.commit()
        return jsonify({"message": "Employee added successfully"}), 200
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
@app.route('/api/enmploy/<ID>', methods=['PUT','PATCH'])
@login_required
def employ_update(ID):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    employee = db.query(Employee).get(ID)
    if not employee:
        return jsonify({"error": "Employee not found"}), 404

    def parse_date(date_str):
        if date_str:
            try:
                return datetime.strptime(date_str, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                return None
        return None

    # Update fields
    for field in ['fname', 'mname', 'lname', 'gender', 'fanID', 'birthdate', 'phone_number', 'edu_level', 'profession', 'work_experience', 'group_name', 'position_in_group', 'join_year', 'work_place', 'work_place_name', 'salary', 'werada', 'kebele', 'house_number']:
        if field in data:
            if field in ['birthdate', 'join_year']:
                setattr(employee, field, parse_date(data[field]))
            else:
                setattr(employee, field, data[field])

    db.commit()
    return jsonify({"message": "Employee updated successfully"}), 200

@app.route('/api/enmploy/delete/<ID>', methods=['DELETE'])
@login_required
def employ_delete(ID):
    employee = db.query(Employee).get(ID)
    if not employee:
        return jsonify({"error": "Employee not found"}), 404

    db.delete(employee)
    db.commit()
    return jsonify({"message": "Employee deleted successfully"}), 200


@app.route('/api/enmploy/<ID>', methods=['GET'])
@login_required
def employ_get(ID):
    employee = db.query(Employee).get(ID)
    if not employee:
        return jsonify({"error": "Employee not found"}), 404
    
    return jsonify({
        'fname': employee.fname,
        'mname': employee.mname,
        'lname': employee.lname,
        'gender': employee.gender,
        'fanID': employee.fanID,
        'birthdate': employee.birthdate.strftime('%Y-%m-%d') if employee.birthdate else None,
        'phone_number': employee.phone_number,
        'edu_level': employee.edu_level,
        'profession': employee.profession,
        'work_experience': employee.work_experience,
        'group_name': employee.group_name,
        'position_in_group': employee.position_in_group,
        'join_year': employee.join_year.strftime('%Y-%m-%d') if employee.join_year else None,
        'work_place': employee.work_place,
        'work_place_name': employee.work_place_name,
        'salary': employee.salary,
        'werada': employee.werada,
        'kebele': employee.kebele,
        'house_number': employee.house_number
    }), 200



if __name__ == '__main__':
    app.run(debug=True)
