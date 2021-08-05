import Proctor_Board.Project.app as app
import bcrypt

from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_wtf import FlaskForm
from base64 import b64encode
from wtforms import StringField, SelectField, PasswordField
from wtforms.validators import InputRequired, EqualTo, length
from flask_login import login_required, login_user

Principals = Blueprint('Principal', __name__, template_folder="templates", static_folder="static")

#Principal_Login
class PrincipalLoginForm(FlaskForm):
    EmployeeID = StringField()
    Password = PasswordField()

@Principals.route("/")
@login_required
@app.role_required('Principal')
def PrincipalHome():
    Students = app.Student_Personal.query.all()
    if Students:
        return render_template("PrincipalHome.html", data=Students, count=0)
    return render_template("PrincipalHome.html")

@Principals.route("/display/<id>", methods = ['POST', 'GET'])
def select(id):
    if id:
        Stu_Personal = app.Student_Personal.query.filter_by(USN = id).first()
        Stu_Family = app.Student_Family.query.filter_by(USN = id).first()
        Stu_Marks = app.Marks.query.filter_by(USN=id).all()
        if Stu_Personal and Stu_Family:
            image = b64encode(Stu_Personal.Image).decode("utf-8")
            return render_template("PrincipalDisplay.html", data = Stu_Personal, image=image, data2 = Stu_Family, datamarks = Stu_Marks)
        else:
            "No data found"
    return "Else display"

@Principals.route("/ForgotPassword", methods=['GET','POST'])
def ForgotPassword():
    if request.method == 'POST':
        USN = request.form['Eid'].upper()
        if request.form.get('SendUSN', None):
            Principal = app.Proctor.query.filter_by(EmployeeID = USN).first()
            return render_template("PrincipalForgotPassword.html", data = Principal)
        if request.form.get('ChangePassword', None):
            P1 = request.form['Password']
            P2 = request.form['Confirm_Password']
            PA1 = request.form['PasswordA1']
            PA2 = request.form['PasswordA2']
            USN = request.form['Eid'].upper()
            Principal = app.Proctor.query.filter_by(EmployeeID = USN).first()
            if P1 == P2:
                if Principal.PasswordA1 == PA1 and Principal.PasswordA2 == PA2:
                    Principal.Password = bcrypt.hashpw(P1.encode('utf-8'), bcrypt.gensalt())
                    app.db.session.commit()
                    return redirect(url_for('Principal.PrincipalLogin'))
                else:
                    flash("Check Answers again")
                    return render_template("StudentForgotPassword.html")
            else:
                flash("Both the password should same")
                return render_template("PrincipalForgotPassword.html", data=Principal)
    return render_template("PrincipalForgotPassword.html")

#Principal_Login
@Principals.route("/PrincipalLogin", methods=['POST', 'GET'])
def PrincipalLogin():
    principalloginform = PrincipalLoginForm(request.form)
    if request.method == "POST":
        EmployeeID = principalloginform.EmployeeID.data.upper()
        session['Usertype'] = "Proctor"
        Proctor = app.Proctor.query.filter_by(EmployeeID = EmployeeID, Status = "Active").first()
        if Proctor:
            if bcrypt.checkpw(principalloginform.Password.data.encode('utf-8'), Proctor.Password):
                login_user(Proctor)
                return redirect(url_for("Principal.PrincipalHome"))
        else:
            return "Check Username & Password"

    else:
        return render_template("PrincipalLogin.html", form=principalloginform)
