import Proctor_Board.Project.app as app
import bcrypt

from flask import Blueprint, render_template, flash, session, redirect, url_for, request
from datetime import datetime
from base64 import b64encode
from flask_login import login_required, login_user
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, PasswordField
from sqlalchemy import and_

ChiefProctors = Blueprint('ChiefProctor', __name__, template_folder="templates", static_folder="static")


#Proctor_Login
class ChiefProctorLoginForm(FlaskForm):
    EmployeeID = StringField()
    Password = PasswordField()


@ChiefProctors.route("/")
@login_required
@app.role_required('ChiefProctor')
def home():
    Announcement = app.Announcement.query.all()
    return render_template("ChiefProctorHome.html", data = Announcement)

@ChiefProctors.route("/AddAnnouncement", methods=['post' , 'get'])
@login_required
@app.role_required("ChiefProctor")
def AddAnnouncement():
    Date = datetime.now()
    Announcement = request.form['inputAnnouncement']
    Add_Announcement = app.Announcement(Date, Announcement, 'Active')
    app.db.session.add(Add_Announcement)
    app.db.session.commit()
    flash("Added")
    return redirect(url_for('ChiefProctor.home'))

@ChiefProctors.route("/RemoveAnnouncement/<id>", methods=['POST','GET'])
@login_required
@app.role_required("ChiefProctor")
def RemoveAnnouncement(id):
    Remove = app.Announcement.query.filter_by(_id = int(id)).first()
    app.db.session.delete(Remove)
    app.db.session.commit()
    return redirect(url_for('ChiefProctor.home'))

@ChiefProctors.route("/Assign", methods=['GET','POST'])
@login_required
@app.role_required("ChiefProctor")
def Assign():
    Students = app.Student_Personal.query.filter_by(Status = "Active").all()
    Proctors = app.Proctor.query.filter_by(Status = "Active").all()
    if request.method == 'POST':
        if request.form['Proctor_Name'] == "name":
            flash("Select Proctor")
            return render_template("ChiefProctorAssign.html", Student_data=Students, Proctor_data=Proctors)
        else:
            Proctor_ID = request.form['Proctor_Name']
            Proctor = app.Proctor.query.filter_by(EmployeeID = Proctor_ID).first()
            ID = request.form.getlist('Checked_USN')
            Students = app.Student_Personal.query.filter_by(Status = "Active").all()
            for rows in Students:
                if rows.USN in ID:
                    rows.Proctor = Proctor.Name
                    rows.ProctorID = Proctor_ID
                    app.db.session.commit()
            print(ID)
            return render_template("ChiefProctorAssign.html", Student_data = Students, Proctor_data = Proctors)
    return render_template("ChiefProctorAssign.html", Student_data = Students, Proctor_data = Proctors)

@ChiefProctors.route("/quicksearch", methods=['GET','POST'])
@login_required
@app.role_required("ChiefProctor")
def quicksearch():
    if request.method == "POST":
        type = request.form['type']
        string = request.form['string']
        if type == "Hobbies":
            Students = app.Student_Personal.query.filter(app.Student_Personal.Hobbies.like("%" + string + "%")).filter_by(Status = "Active").all()
        elif type == "BloodGroup":
            Students = app.Student_Personal.query.filter(app.Student_Personal.BloodGroup.like("%" + string + "%")).filter_by(Status="Active").all()
        Proctors = app.Proctor.query.filter_by(Status="Active").all()
        return render_template("ChiefProctorAssign.html", Student_data=Students, Proctor_data=Proctors)


#Display_Student_Details
@ChiefProctors.route("/display/<id>", methods = ['POST', 'GET'])
@login_required
@app.role_required('ChiefProctor')
def select(id):
    if id:
        Stu_Personal = app.Student_Personal.query.filter_by(USN = id).first()
        Stu_Family = app.Student_Family.query.filter_by(USN = id).first()
        Stu_Marks = app.Marks.query.filter_by(USN=id).all()
        Stu_Achievements = app.Achievements.query.filter_by(USN=id).all()
        Stu_Meeting = app.Meeting.query.filter_by(USN=id).all()
        if Stu_Personal and Stu_Family:
            image = b64encode(Stu_Personal.Image).decode("utf-8")
            return render_template("ChiefProctorGetReport.html", data = Stu_Personal, image=image, data2 = Stu_Family, datamarks = Stu_Marks, datameetings = Stu_Meeting, dataachievements = Stu_Achievements)
        else:
            flash("No data found")
            return redirect(url_for('ChiefProctor.home'))
    return redirect(url_for('ChiefProctor.home'))

@ChiefProctors.route("/ShowProctors", methods=['POST','GET'])
@login_required
@app.role_required("ChiefProctor")
def ShowProctors():
    Proctors = app.Proctor.query.filter_by(Status = "Active").all()
    return render_template("ChiefProctorShowProctors.html",Proctor_data=Proctors)

@ChiefProctors.route("/RemoveProctors", methods=['POST','GET'])
@login_required
@app.role_required("ChiefProctor")
def RemoveProctors():
    id = request.form['hidden_Removal_Id'].upper()
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
@login_required
@app.role_required("ChiefProctor")
def RemoveStudents():
    id = request.form['hidden_Removal_Id'].upper()
    message = request.form['Removal_Message']
    Student = app.Student_Personal.query.filter_by(USN = id).first()
    Student.RemoveMsg = message
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
                flash("Check Password")
                return redirect(url_for("ChiefProctor.ChiefProctorLogin"))
        else:
            flash("Check Username")
            return redirect(url_for("ChiefProctor.ChiefProctorLogin"))

    else:
        return render_template("ChiefProctorLogin.html", form=chiefproctorloginform)


@ChiefProctors.route("/ForgotPassword", methods=['GET','POST'])
def ForgotPassword():
    if request.method == 'POST':
        USN = request.form['USN'].upper()
        if request.form.get('SendUSN', None):
            Proctor = app.Proctor.query.filter_by(EmployeeID = USN).first()
            return render_template("ChiefProctorForgotPassword.html", data = Proctor)
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

@ChiefProctors.route("/viewcertificate/<id>", methods = ['POST', 'GET'])
@login_required
@app.role_required("ChiefProctor")
def viewcertificate(id):
    certificate = app.Achievements.query.filter_by(_id=id).first()
    image = b64encode(certificate.Certificates).decode("utf-8")
    return render_template("showcertificate.html", image = image)