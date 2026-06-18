from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import base64
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
from io import BytesIO

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


@app.context_processor
def inject_now():
    from datetime import datetime
    return {'now': datetime.now()}

@login_manager.user_loader
def user_loader(user_id):
    return db.query(User).get(int(user_id))

# views

@app.route('/')
def index():
    return redirect('/login')


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
            return redirect('/dashboard')
        else:
            flash('Incorrect user name or password')
            return render_template('login.html')

# auth

@login_required
@app.route('/upload_multiple_docs/<int:employee_id>', methods=['POST'])
def upload_multiple_docs(employee_id):
    employee = db.query(Employee).filter_by(id=employee_id).first()
    if not employee:
        flash("Employee not found", "error")
        return redirect('/action')

    files = request.files.getlist('docs')
    if not files:
        flash("No files uploaded", "error")
        return redirect(f'/employee/{employee_id}')

    for file in files:
        if file and file.filename:
            filename = secure_filename(file.filename)
            os.makedirs('static/docs', exist_ok=True)
            file_path = os.path.join('static/docs', filename)
            file.save(file_path)

            doc = Doc(
                employee_id=employee_id,
                name=filename,
                url=f"docs/{filename}",
                file_type=file.content_type
            )
            db.add(doc)

    try:
        db.commit()
        flash("Documents uploaded successfully", "success")
    except Exception as e:
        db.rollback()
        flash(f"Error uploading documents: {str(e)}", "error")

    return redirect(f'/employee/{employee_id}')


@login_required
@app.route('/dashboard')
def dashboard():
    number_of_employee = len(db.query(Employee).all())
    female_employee = len(db.query(Employee).filter_by(gender="ሴት").all())
    male_employee = len(db.query(Employee).filter_by(gender="ወነድ").all())

    return render_template(
        "dashboard.html", 
        number_of_employee=number_of_employee, 
        female_employee=female_employee, 
        male_employee=male_employee
    )


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


@login_required
@app.route('/setting', methods=['GET', 'POST'])
def setting():
    user_info = db.query(User).filter_by(is_default_user=1).first()
    if not user_info:
        flash("User not found", "error")
        return redirect('/dashboard')
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate email
        if not email:
            flash("Email is required", "error")
            return redirect('/setting')
        
        # Check if password is provided and matches
        if password:
            if password != confirm_password:
                flash("Passwords do not match", "error")
                return redirect('/setting')
            if len(password) < 8:
                flash("Password must be at least 8 characters long", "error")
                return redirect('/setting')
        
        # Update user info
        user_info.email = email
        if password:  # Only update password if provided
            user_info.password = password  # Consider hashing the password!
        
        try:
            db.commit()
            flash("Profile updated successfully", "success")
            return redirect('/setting')
        except Exception as e:
            db.rollback()
            flash(f"Error updating profile: {str(e)}", "error")
            return redirect('/setting')
    
    return render_template('admin_profile.html', user_info=user_info)


@app.route("/report")
@login_required
def report():
    employees = db.query(Employee).all()
    return render_template('report.html', employees=employees)

@app.route("/report/download")
@login_required
def report_download():
    employees = db.query(Employee).all()
    
    # Create PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=0.3*inch,
        leftMargin=0.3*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    
    # Register a font that supports Amharic
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    
    # Make sure the fonts directory exists
    os.makedirs('static/fonts', exist_ok=True)
    
    # Try different font paths
    font_paths = [
        os.path.join('static', 'fonts', 'AbyssinicaSIL-Regular.ttf'),
        os.path.join('static', 'fonts', 'Kefa.ttf'),
        os.path.join('static', 'fonts', 'Ethiopic.ttf'),
        os.path.join('static', 'fonts', 'NotoSansEthiopic-Regular.ttf'),
        '/usr/share/fonts/truetype/abyssinica/AbyssinicaSIL-Regular.ttf',
        '/usr/share/fonts/truetype/kefa/Kefa.ttf',
        '/usr/share/fonts/truetype/ethiopia/ethiopia.ttf',
        '/usr/share/fonts/truetype/noto/NotoSansEthiopic-Regular.ttf',
        '/System/Library/Fonts/Supplemental/Arial.ttf',  # macOS
    ]
    
    font_registered = False
    font_name = 'Helvetica'  # fallback font
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont('AmharicFont', font_path))
                font_name = 'AmharicFont'
                font_registered = True
                print(f"Successfully loaded font from: {font_path}")
                break
            except Exception as e:
                print(f"Failed to load font from {font_path}: {e}")
                continue
    
    if not font_registered:
        print("Warning: No Amharic font found. Using Helvetica fallback. Amharic characters may not display correctly.")
        print("Please download Abyssinica SIL font from: https://abyssinica.com/")
        print("And place it in: static/fonts/AbyssinicaSIL-Regular.ttf")
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Create custom styles with the Amharic font
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        alignment=TA_CENTER,
        fontName=font_name,
        fontSize=16
    )
    
    date_style = ParagraphStyle(
        'DateStyle',
        parent=styles['Normal'],
        alignment=TA_CENTER,
        fontSize=10,
        textColor=colors.gray,
        fontName=font_name
    )
    
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=7
    )
    
    cell_style = ParagraphStyle(
        'CellStyle',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=6
    )
    
    # Build content
    content = []
    
    # Title
    title = Paragraph("Employee Report", title_style)
    content.append(title)
    content.append(Spacer(1, 0.2*inch))
    
    # Date
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    date_para = Paragraph(f"Generated on: {date_str}", date_style)
    content.append(date_para)
    content.append(Spacer(1, 0.3*inch))
    
    # Prepare table data
    table_data = []
    
    # Headers
    headers = [
        '#', 'ስም', 'የአባት', 'የአያት', 'ጾታ', 'ፋይዳ', 'የትውልድ',
        'ስልክ', 'የት/ት', 'መስክ', 'ልምድ', 'የቤተሰብ', 'ኃላፊነት',
        'ተቀላቀለ', 'ተቋም', 'ህብረት', 'ደመወዝ', 'ወረዳ', 'ቀበሌ', 'ቤት ቁ'
    ]
    table_data.append(headers)
    
    # Data rows
    for idx, emp in enumerate(employees, 1):
        row = [
            str(idx),
            str(emp.fname or '-'),
            str(emp.mname or '-'),
            str(emp.lname or '-'),
            str(emp.gender or '-'),
            str(emp.fanID or '-'),
            emp.birthdate.strftime('%Y-%m-%d') if emp.birthdate else '-',
            str(emp.phone_number or '-'),
            str(emp.edu_level or '-'),
            str(emp.profession or '-'),
            str(emp.work_experience or '-'),
            str(emp.group_name or '-'),
            str(emp.position_in_group or '-'),
            emp.join_year.strftime('%Y-%m-%d') if emp.join_year else '-',
            str(emp.work_place or '-'),
            str(emp.work_place_name or '-'),
            f"{emp.salary:,}" if emp.salary else '-',
            str(emp.werada or '-'),
            str(emp.kebele or '-'),
            str(emp.house_number or '-'),
        ]
        table_data.append(row)
    
    # Create table with custom font for Amharic support
    table = Table(table_data, repeatRows=1)
    
    # Style the table
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), font_name),
        ('FONTSIZE', (0, 0), (-1, 0), 7),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 6),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 1), (-1, -1), font_name),
    ])
    table.setStyle(style)
    content.append(table)
    
    # Build PDF
    doc.build(content)
    buffer.seek(0)
    
    # Generate filename
    filename = f"employee_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    # Return file for download
    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )

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
    photo_path = f"static/{employee.photo_url}"

    os.remove(photo_path)

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
