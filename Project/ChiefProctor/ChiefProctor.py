import Proctor_Board.Project.app as app
import bcrypt

from flask import Blueprint, render_template, flash, session, redirect, url_for, request
from datetime import datetime
from base64 import b64encode
from flask_login import login_required, login_user
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, PasswordField
from wtforms import StringField, SelectField, PasswordField

ChiefProctors = Blueprint('ChiefProctor', __name__, template_folder="templates", static_folder="static")


#Proctor_Login
class ChiefProctorLoginForm(FlaskForm):
    EmployeeID = StringField()
    Password = PasswordField()


@ChiefProctors.route("/")
def home():
    Announcement = app.Announcement.query.all()
    return render_template("ChiefProctorHome.html", data = Announcement)

@ChiefProctors.route("/AddAnnouncement", methods=['post' , 'get'])
def AddAnnouncement():
    Date = datetime.now()
    Announcement = request.form['inputAnnouncement']
    Add_Announcement = app.Announcement(Date, Announcement, 'Active')
    app.db.session.add(Add_Announcement)
    app.db.session.commit()
    flash("Added")
    return redirect(url_for('ChiefProctor.home'))

@ChiefProctors.route("/RemoveAnnouncement/<id>", methods=['POST','GET'])
def RemoveAnnouncement(id):
    Remove = app.Announcement.query.filter_by(_id = int(id)).first()
    app.db.session.delete(Remove)
    app.db.session.commit()
    return redirect(url_for('ChiefProctor.home'))

@ChiefProctors.route("/Assign", methods=['GET','POST'])
def Assign():
    Students = app.Student_Personal.query.filter_by(Status = "Active").all()
    Proctors = app.Proctor.query.filter_by(Status = "Active").all()
    if request.method == 'POST':
        Proctor_ID = request.form['Proctor_Name']
        Proctor = app.Proctor.query.filter_by(EmployeeID = Proctor_ID).first()
        ID = request.form.getlist('Checked_USN')
        Students = app.Student_Personal.query.all()
        for rows in Students:
            if rows.USN in ID:
                rows.Proctor = Proctor.Name
                rows.ProctorID = Proctor_ID
                app.db.session.commit()
        print(ID)
        return render_template("ChiefProctorAssign.html", Student_data = Students, Proctor_data = Proctors)
    return render_template("ChiefProctorAssign.html", Student_data = Students, Proctor_data = Proctors)

#Display_Student_Details
@ChiefProctors.route("/display/<id>", methods = ['POST', 'GET'])
def select(id):
    if id:
        Stu_Personal = app.Student_Personal.query.filter_by(USN = id).first()
        Stu_Family = app.Student_Family.query.filter_by(USN = id).first()
        Stu_Marks = app.Marks.query.filter_by(USN=id).all()
        if Stu_Personal and Stu_Family:
            image = b64encode(Stu_Personal.Image).decode("utf-8")
            return render_template("ChiefProctorGetReport.html", data = Stu_Personal, image=image, data2 = Stu_Family, datamarks = Stu_Marks)
        else:
            "No data found"
    return "Else display"

@ChiefProctors.route("/ShowProctors", methods=['POST','GET'])
def ShowProctors():
    Proctors = app.Proctor.query.filter_by(Status = "Active").all()
    return render_template("ChiefProctorShowProctors.html",Proctor_data=Proctors)

@ChiefProctors.route("/RemoveProctors", methods=['POST','GET'])
def RemoveProctors():
    id = request.form['Removal_User_ID'].upper()
    message = request.form['Removal_Message']
    Proctor = app.Proctor.query.filter_by(EmployeeID = id).first()
    name = Proctor.Name
    id = Proctor.EmployeeID
    Proctor.RemovalMessage = message
    Proctor.Status = 'Removed'
    app.db.session.commit()
    Students = app.Student_Personal.query.filter_by(Proctor = name, ProctorID = id).all()
    for rows in Students:
        print(rows)
        rows.Proctor = ""
        rows.ProctorID = ""
        app.db.session.commit()
    return redirect(url_for("ChiefProctor.ShowProctors"))

@ChiefProctors.route("/RemoveStudents", methods=['POST','GET'])
def RemoveStudents():
    id = request.form['Removal_User_ID'].upper()
    message = request.form['Removal_Message']
    Student = app.Student_Personal.query.filter_by(USN = id).first()
    Student.RemovalMessage = message
    Student.Status = 'Removed'
    app.db.session.commit()
    return redirect(url_for("ChiefProctor.Assign"))

#Proctor_Login
@ChiefProctors.route("/ChiefProctorLogin", methods=['POST', 'GET'])
def ChiefProctorLogin():
    chiefproctorloginform = ChiefProctorLoginForm(request.form)
    if request.method == "POST":
        EmployeeID = chiefproctorloginform.EmployeeID.data.upper()
        session['Usertype'] = "Proctor"
        Proctor = app.Proctor.query.filter_by(EmployeeID = EmployeeID, Status = "Active").first()
        if Proctor:
            if bcrypt.checkpw(chiefproctorloginform.Password.data.encode('utf-8'), Proctor.Password):
                login_user(Proctor)
                return redirect(url_for("ChiefProctor.home"))
        else:
            return "Check Username & Password"

    else:
        return render_template("ChiefProctorLogin.html", form=chiefproctorloginform)


@ChiefProctors.route("/ForgotPassword", methods=['GET','POST'])
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
                    return redirect(url_for('ChiefProctor.ChiefProctorLogin'))
                else:
                    flash("Check Answers again")
                    return render_template("ChiefProctorForgotPassword.html")
            else:
                flash("Both the password should same")
                return render_template("ChiefProctorForgotPassword.html", data=Proctor)
    return render_template("ChiefProctorForgotPassword.html")


