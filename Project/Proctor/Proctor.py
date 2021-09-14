import bcrypt

import Proctor_Board.Project.app as app

from flask import Blueprint, redirect, request, render_template, url_for, flash, session
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, PasswordField
from wtforms.validators import InputRequired, EqualTo, length
from flask_login import login_required, login_user
from datetime import datetime
from flask_login import current_user
from base64 import b64encode

Proctors = Blueprint('Proctor', __name__, template_folder="templates", static_folder="static")

#Forms
#PRoctor_Details
class ProctorRegistrationForm(FlaskForm):
    Name = StringField('Name', validators=[InputRequired(message='Required'), length(min=3, max=30, message="Name should be below 30 Characters")])
    EmployeeID = StringField('EmployeeID', validators=[InputRequired(message='Required'), length(min=3, max=30, message="EmployeeID should be below 30 Characters")])
    Department = SelectField(choices=app.Courses)
    Mobile = StringField(validators=[InputRequired(message="Mobile Number Required")])
    BloodGroup = SelectField(choices=app.Blood_Group)
    Password = PasswordField('Password', validators=[InputRequired(message='Required')])
    Confirm_Password = StringField(validators=[InputRequired(message='Required'), EqualTo('Password', message="Both the password should same")])
    PasswordQ1 = SelectField(choices=app.Password_Recover_Questions)
    PasswordA1 = StringField(validators=[InputRequired(message="Mobile Number Required")])
    PasswordQ2 = SelectField(choices=app.Password_Recover_Questions)
    PasswordA2 = StringField(validators=[InputRequired(message="Mobile Number Required")])

#Proctor_Login
class ProctorLoginForm(FlaskForm):
    EmployeeID = StringField()
    Password = PasswordField()



@Proctors.route("/ProctorRegister", methods = ['post','get'])
def ProctorRegister():
    proctorregister = ProctorRegistrationForm(request.form)
    if proctorregister.validate_on_submit():
        Name = proctorregister.Name.data
        EmployeeID = proctorregister.EmployeeID.data.upper()
        Department = proctorregister.Department.data
        Mobile = proctorregister.Mobile.data
        BloodGroup = proctorregister.BloodGroup.data
        Password = bcrypt.hashpw(proctorregister.Password.data.encode('utf-8'), bcrypt.gensalt())
        PasswordQ1 = proctorregister.PasswordQ1.data
        PasswordA1 = proctorregister.PasswordA1.data
        PasswordQ2 = proctorregister.PasswordQ2.data
        PasswordA2 = proctorregister.PasswordA2.data

        proctor = app.Proctor.query.filter_by(EmployeeID = EmployeeID).first()

        if proctor:
            flash("User Already exist try login")
            return redirect(url_for('Proctor.ProctorRegister'))

        else:
            new_proctor = app.Proctor(Name, EmployeeID, Department, Mobile, BloodGroup,Password, PasswordQ1, PasswordA1, PasswordQ2, PasswordA2, '','Proctor','Active')
            app.db.session.add(new_proctor)
            app.db.session.commit()
            flash("User Added")
        return redirect(url_for('Proctor.ProctorRegister'))
    return render_template("ProctorRegister.html", form = proctorregister)

#Proctor_Login
@Proctors.route("/ProctorLogin", methods=['POST', 'GET'])
def ProctorLogin():
    proctorloginform = ProctorLoginForm(request.form)
    if request.method == "POST":
        EmployeeID = proctorloginform.EmployeeID.data.upper()
        session['Usertype'] = "Proctor"
        Proctor = app.Proctor.query.filter_by(EmployeeID = EmployeeID, Status = "Active").first()
        if Proctor:
            if bcrypt.checkpw(proctorloginform.Password.data.encode('utf-8'), Proctor.Password):
                app.Usertype = "Proctor"
                login_user(Proctor)
                return redirect(url_for("Proctor.ProctorHome"))
            else:
                return "Check Username & Password"
        else:
            return "Check Username & Password"

    else:
        return render_template("ProctorLogin.html", form=proctorloginform)

@Proctors.route("/")
@Proctors.route("/ProctorHome")
@login_required
@app.role_required('Proctor')
def ProctorHome():
    Students = app.Student_Personal.query.filter_by(ProctorID = current_user.EmployeeID, Status='Active').all()
    Announcements = app.Announcement.query.all()
    if Students:
        return render_template("ProctorHome.html", data=Students, count=0, data1 = Announcements)
    return render_template("ProctorHome.html", data=Students, count=0, data1 = Announcements)


@Proctors.route("/ProctorMarks", methods=['post','get'])
@login_required
@app.role_required('Proctor')
def ProctorMarks():
    if request.method == 'POST':
        if request.form.get('Search', None):
            if request.form['inputUSN'] == "":
                flash("Enter USN")
                return redirect(url_for("Proctor.ProctorMarks"))
            else:
                USN = request.form['inputUSN'].upper()
                print(current_user._id)
                Student_Detail = app.Student_Personal.query.filter_by(USN = USN, ProctorID = current_user.EmployeeID, Status='Active').first()
                if Student_Detail:
                    session['temp_Name'] = Student_Detail.Name
                    session['temp_USN'] = Student_Detail.USN
                    session['temp_Dept'] = Student_Detail.ProgramEnrolled
                    session['temp_Semester'] = Student_Detail.Semester
                    sem = str(Student_Detail.Semester)
                    classs = Student_Detail.ProgramEnrolled
                    sub = app.panda_df[sem][classs]
                    session['Subjects'] = sub
                    return render_template("ProctorMarks.html", data = Student_Detail, data2=sub)
                else :
                    flash("Currently you are unable to view this student")
                    return redirect(url_for("Proctor.ProctorMarks"))

        if request.form.get('Submit', None):
            USN = session['temp_USN']
            Name = session['temp_Name']
            Dept = session['temp_Dept']
            Semester = session['temp_Semester']
            full_Marks = request.form.getlist('inputMarks[]')
            full_Remarks = request.form.getlist('inputRemarks[]')
            count = 0
            for subject in session['Subjects']:
                Marks = full_Marks[count]
                Remarks = full_Remarks[count]
                Marks_Update = app.Marks(Name, USN, Dept, Semester, subject, Marks, Remarks)
                app.db.session.add(Marks_Update)
                app.db.session.commit()
                count = count+1
            return render_template("ProctorMarks.html")
    return render_template("ProctorMarks.html")


@Proctors.route("/ProctorMeeting", methods=['post','get'])
@login_required
@app.role_required('Proctor')
def ProctorMeeting():
    if request.method == 'POST':
        if request.form.get('Search', None):
            if request.form['inputUSN'] == "":
                flash("Enter USN")
                return redirect(url_for("Proctor.ProctorMeeting"))
            else:
                USN = request.form['inputUSN'].upper()
                Student_Detail = app.Student_Personal.query.filter_by(USN=USN, ProctorID = current_user.EmployeeID, Status='Active').first()
                if Student_Detail:
                    session['temp_Name'] = Student_Detail.Name
                    session['temp_USN'] = Student_Detail.USN
                    session['temp_Dept'] = Student_Detail.ProgramEnrolled
                    session['temp_Semester'] = Student_Detail.Semester
                    return render_template("ProctorMeeting.html", data=Student_Detail)
                else:
                    flash("Currently you are unable to view this student")
                    return redirect(url_for("Proctor.ProctorMeeting"))

        if request.form.get('Submit', None):
            USN = session['temp_USN']
            Name = session['temp_Name']
            Dept = session['temp_Dept']
            Semester = session['temp_Semester']
            Exam = request.form['Exam']
            Achievements = request.form['Achievements']
            GoalSetting = request.form['GoalSetting']
            Workplan = request.form['Workplan']
            Datetime = datetime.now()
            Meeting = app.Meeting(Name, USN, Dept, Semester, Exam, Achievements, GoalSetting, Workplan, Datetime)
            app.db.session.add(Meeting)
            print("done")
            app.db.session.commit()
            return render_template("ProctorMeeting.html")

    return render_template("ProctorMeeting.html")


@Proctors.route("/ForgotPassword", methods=['GET','POST'])
def ForgotPassword():
    if request.method == 'POST':
        USN = request.form['USN'].upper()
        if request.form.get('SendUSN', None):
            Proctor = app.Proctor.query.filter_by(EmployeeID = USN).first()
            return render_template("ProctorForgotPassword.html", data = Proctor)
        if request.form.get('ChangePassword', None):
            P1 = request.form['Password']
            P2 = request.form['Confirm_Password']
            PA1 = request.form['PasswordA1']
            PA2 = request.form['PasswordA2']
            USN = request.form['USN'].upper()
            Proctor = app.Proctor.query.filter_by(EmployeeID=USN).first()
            if P1 == P2:
                if Proctor.PasswordA1 == PA1 and Proctor.PasswordA2 == PA2:
                    Proctor.Password = bcrypt.hashpw(P1.encode('utf-8'), bcrypt.gensalt())
                    app.db.session.commit()
                    return redirect(url_for('Proctor.ProctorLogin'))
                else:
                    flash("Check Answers again")
                    return render_template("ProctorForgotPassword.html")
            else:
                flash("Both the password should same")
                return render_template("ProctorForgotPassword.html", data=Proctor)
    return render_template("ProctorForgotPassword.html")

#Display_Student_Details
@Proctors.route("/display/<id>", methods = ['POST', 'GET'])
@login_required
@app.role_required('Proctor')
def select(id):
    if id:
        Stu_Personal = app.Student_Personal.query.filter_by(USN = id).first()
        if not Stu_Personal:
            flash("No student found")
            return redirect(url_for('Proctor.ProctorHome'))
        if Stu_Personal.ProctorID != current_user.EmployeeID:
            flash("Currently you are not able to view this student")
            return redirect(url_for('Proctor.ProctorHome'))
        Stu_Family = app.Student_Family.query.filter_by(USN = id).first()
        Stu_Marks = app.Marks.query.filter_by(USN=id).all()
        Stu_Achievements = app.Achievements.query.filter_by(USN=id).all()
        Stu_Meeting = app.Meeting.query.filter_by(USN=id).all()
        if Stu_Personal and Stu_Family:
            image = b64encode(Stu_Personal.Image).decode("utf-8")
            return render_template("ProctorGetReport.html", data = Stu_Personal, image=image, data2 = Stu_Family, datamarks = Stu_Marks, datameetings = Stu_Meeting, dataachievements = Stu_Achievements)
        else:
            flash("No data found")
            return redirect(url_for('Proctor.ProctorHome'))
    flash("Else display")
    return redirect(url_for('Proctor.ProctorHome'))

@Proctors.route("/viewcertificate/<id>", methods = ['POST', 'GET'])
@app.role_required("Proctor")
@login_required
def viewcertificate(id):
    certificate = app.Achievements.query.filter_by(_id=id).first()
    image = b64encode(certificate.Certificates).decode("utf-8")
    return render_template("Proctorshowcertificate.html", image = image)

