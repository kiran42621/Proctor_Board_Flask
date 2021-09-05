import bcrypt
from flask import Blueprint
from flask import render_template, redirect, url_for, flash, request, session
from flask_wtf import Form, FlaskForm
from wtforms import StringField, SelectField, RadioField, IntegerField, FileField, PasswordField, FloatField
from wtforms.validators import InputRequired, EqualTo, length, NumberRange, Optional
from wtforms.fields.html5 import DateField
from flask_login import login_required, current_user, login_user
from werkzeug.utils import secure_filename
from base64 import b64encode
import Proctor_Board.Project.app as app

Students = Blueprint('Student', __name__, template_folder="templates", static_folder="static")

#Check File Type
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.Allowed_Extensions

# Forms
# Student_Register_Form
class StudentRegisterForm(Form):
    Name = StringField('Name', validators=[InputRequired(message='Required'), length(min=3, max=30, message="Name should be below 30 Characters")])
    USN = StringField('USN', validators=[InputRequired(message='USN Required')])
    Prog_Enrolled = SelectField(choices=app.Courses)
    Year = StringField('Year', validators=[InputRequired(message='Required'), length(min=4, max=4, message="Year should be 4 Characters")])
    Semester = SelectField(choices=app.Semester, validators=[InputRequired(message='Required')])
    Gender = RadioField(choices=[('Male', 'Male'), ('Female', 'Female')], validators=[InputRequired(message='Must select any one option')])
    Mobile = StringField('Mobile', validators=[InputRequired(message='Mobile Number Required'), length(min=10, max=12, message="Mobile Number should be 10 - 12 characters")])
    DOB = DateField('Date', format="%Y-%m-%d", validators=[InputRequired(message='Must Choose Date')])
    BloodGroup = SelectField(choices=app.Blood_Group)
    Image = FileField(validators=[InputRequired(message='Required')])
    Email = StringField(validators=[InputRequired(message='Required')])
    Address = StringField(validators=[InputRequired(message='Required'), length(max=130,message="Address should be below 130 Characters")])
    City = StringField(validators=[InputRequired(message='Required'), length(max=30,message="City should be below 30 Characters")])
    State = StringField(validators=[InputRequired(message='Required'), length(max=20,message="State should be below 20 Characters")])
    Zipcode = StringField()
    Hobbies = StringField([InputRequired(message='Required'), length(max=40, message="Hobbies should be below 30 Characters")])
    Password = PasswordField('Password', validators=[InputRequired(message='Required')])
    Confirm_Password = PasswordField(validators=[InputRequired(message='Required'), EqualTo('Password', message="Both the password should same")])
    PasswordQ1 = SelectField(choices=app.Password_Recover_Questions)
    PasswordA1 = StringField([InputRequired(message='Required')])
    PasswordQ2 = SelectField(choices=app.Password_Recover_Questions)
    PasswordA2 = StringField([InputRequired(message='Required')])

    #Family
    Father_Name = StringField(validators=[Optional()])
    Father_Qualification = StringField(validators=[Optional()])
    Father_Profession = StringField(validators=[Optional()])
    Mother_Name = StringField(validators=[Optional()])
    Mother_Qualification = StringField(validators=[Optional()])
    Mother_Profession = StringField(validators=[Optional()])
    Sibling1_Name = StringField(validators=[Optional()])
    Sibling1_Qualification = StringField(validators=[Optional()])
    Sibling1_Profession = StringField(validators=[Optional()])
    Sibling2_Name = StringField(validators=[Optional()])
    Sibling2_Qualification = StringField(validators=[Optional()])
    Sibling2_Profession = StringField(validators=[Optional()])

    #Academic
    SSLC_Institute = StringField(validators=[InputRequired(message='Required')])
    SSLC_Year = IntegerField(validators=[InputRequired(message='Required')])
    SSLC_Percentage = FloatField(validators=[InputRequired(message='Required')])
    PUC_Institute = StringField(validators=[InputRequired(message='Required')])
    PUC_Year = IntegerField(validators=[InputRequired(message='Required')])
    PUC_Percentage = FloatField(validators=[InputRequired(message='Required')])
    Part_Time_Jobs = StringField(validators=[Optional()])
    Future_Plans = StringField(validators=[Optional()])


#Student_Login_Form
class StudentLoginForm(FlaskForm):
    USN = StringField(validators=[InputRequired(message='Required')])
    Password = PasswordField(validators=[InputRequired(message='Required')])

#Achievements_Form
class AchievementsForm(FlaskForm):
    EventType = SelectField(choices=app.EventType)
    EventName = StringField()
    PrizesWon = StringField()
    Certificates = FileField()


#routes
@Students.route("/", methods=['POST','GET'])
@login_required
@app.role_required("Student")
def home():
    if current_user.RoleID == 'Student':
        achievements = AchievementsForm(request.form)
        if achievements.validate_on_submit():
            EventType = achievements.EventType.data
            EventName = achievements.EventName.data
            PrizesWon = achievements.PrizesWon.data
            pic = request.files['Certificates']
            if pic and allowed_file(pic.filename):
                Certificate = pic.read()
                Certificate_Filename = secure_filename(pic.filename)
                Certificate_Mimetype = pic.mimetype
            else:
                flash("Image should be png, jpg, and jpeg format")
                return render_template("StudentHome.html", form=achievements)
            Achievement = app.Achievements(current_user.Name, current_user.USN, EventType, EventName, PrizesWon, Certificate, Certificate_Filename, Certificate_Mimetype)
            app.db.session.add(Achievement)
            app.db.session.commit()
            flash("Certificate added successfully")
            return render_template("StudentHome.html", form = achievements)
        return render_template("StudentHome.html", form = achievements)

#Student_Register
@Students.route("/ren_Student_Register", methods = ['POST','GET'])
def StudentRegister():
    print(1)
    studentregisterform = StudentRegisterForm()
    print(studentregisterform.Name.errors)
    if studentregisterform.validate_on_submit():
        Name = studentregisterform.Name.data
        USN = (studentregisterform.USN.data).upper()
        ProgramEnrolled = studentregisterform.Prog_Enrolled.data
        Year = studentregisterform.Year.data
        Semester = studentregisterform.Semester.data
        Gender = studentregisterform.Gender.data
        Mobile = studentregisterform.Mobile.data
        DOB = studentregisterform.DOB.data
        BloodGroup = studentregisterform.BloodGroup.data
        Email = studentregisterform.Email.data
        Address = studentregisterform.Address.data
        City = studentregisterform.City.data
        State = studentregisterform.State.data
        Zipcode = studentregisterform.Zipcode.data
        Hobbies = studentregisterform.Hobbies.data
        Password = bcrypt.hashpw(studentregisterform.Password.data.encode('utf-8'), bcrypt.gensalt())
        PasswordQ1 = studentregisterform.PasswordQ1.data
        PasswordA1 = studentregisterform.PasswordA1.data
        PasswordQ2 = studentregisterform.PasswordQ2.data
        PasswordA2 = studentregisterform.PasswordA2.data
        FatherName = studentregisterform.Father_Name.data
        FatherQualification = studentregisterform.Father_Qualification.data
        FatherProfession = studentregisterform.Father_Profession.data
        MotherName = studentregisterform.Mother_Name.data
        MotherQualification = studentregisterform.Mother_Qualification.data
        MotherProfession = studentregisterform.Mother_Profession.data
        Sibling1Name = studentregisterform.Sibling1_Name.data
        Sibling1Qualification = studentregisterform.Sibling1_Qualification.data
        Sibling1Profession = studentregisterform.Sibling1_Profession.data
        Sibling2Name = studentregisterform.Sibling2_Name.data
        Sibling2Qualification = studentregisterform.Sibling2_Qualification.data
        Sibling2Profession = studentregisterform.Sibling2_Profession.data
        SSLCInstitute = studentregisterform.SSLC_Institute.data
        SSLCYear = studentregisterform.SSLC_Year.data
        SSLCPercentage = studentregisterform.SSLC_Percentage.data
        PUCInstitute = studentregisterform.PUC_Institute.data
        PUCYear = studentregisterform.PUC_Year.data
        PUCPercentage = studentregisterform.PUC_Percentage.data
        Part_Time_Jobs = studentregisterform.Part_Time_Jobs.data
        FuturePlans = studentregisterform.Future_Plans.data
        pic = request.files['Image']
        if pic and allowed_file(pic.filename):
            Image = pic.read()
            Image_mime = pic.mimetype
            Image_Filename = secure_filename(pic.filename)
            found_Student = app.Student_Personal.query.filter_by(USN = USN).first()
        else:
            flash("Image should be png, jpg, and jpeg format")
            return render_template("StudentRegister.html", form=studentregisterform)
        if found_Student:
            flash("User Already exist try login")
            return render_template("StudentRegister.html", form = studentregisterform)
        else:
            data1 = app.Student_Personal(Name, USN, ProgramEnrolled, Year, Semester, Gender, Mobile, DOB, BloodGroup, Email, Address, City, State, Zipcode, Hobbies, '', '', Password, PasswordQ1, PasswordA1, PasswordQ2, PasswordA2, Image, Image_mime, Image_Filename, 'Active', '', 'Student')
            data2 = app.Student_Family(Name, USN, FatherName, FatherQualification, FatherProfession, MotherName, MotherQualification, MotherProfession, Sibling1Name, Sibling1Qualification, Sibling1Profession, Sibling2Name, Sibling2Qualification, Sibling2Profession, SSLCInstitute, SSLCYear, SSLCPercentage, PUCInstitute, PUCYear, PUCPercentage, Part_Time_Jobs, FuturePlans)
            print("data 1 done")
            app.db.session.add(data1)
            print("data 2 done")
            app.db.session.add(data2)
            app.db.session.commit()
            flash("Registered Successfully")
            return redirect(url_for("Student.StudentLogin"))

    return render_template("StudentRegister.html", form=studentregisterform)


#Student_Login
@Students.route("/ren_Student_Login", methods=['POST', 'GET'])
def StudentLogin():
    studentloginform = StudentLoginForm(request.form)
    if request.method == 'POST':
        USN = studentloginform.USN.data.upper()
        session['Usertype'] = "Student"
        User = app.Student_Personal.query.filter_by(USN = USN, Status = "Removed").first()
        if User:
            flash(f"You have been removed. Removal message {User.RemoveMsg}.")
            return render_template("StudentLogin.html", form=studentloginform)
        User = app.Student_Personal.query.filter_by(USN = USN).first()
        if User:
            if bcrypt.checkpw(studentloginform.Password.data.encode('utf-8'), User.Password):
                app.Usertype = "Student"
                login_user(User)
                return redirect(url_for('Student.home'))
            else:
                flash("Check Password")
                return render_template("StudentLogin.html", form=studentloginform)

        else:
            flash("Check USN")
            return render_template("StudentLogin.html", form=studentloginform)
    else:
        return render_template("StudentLogin.html", form=studentloginform)



@Students.route("/example", methods=['GET', 'POST'])
def example():
    flash("Submitted")
    return redirect(url_for("Student.StudentRegister"))

@Students.route("/ForgotPassword", methods=['GET','POST'])
def ForgotPassword():
    if request.method == 'POST':
        USN = request.form['USN'].upper()
        if request.form.get('SendUSN', None):
            Student = app.Student_Personal.query.filter_by(USN = USN).first()
            return render_template("StudentForgotPassword.html", data = Student)
        if request.form.get('ChangePassword', None):
            P1 = request.form['Password']
            P2 = request.form['Confirm_Password']
            PA1 = request.form['PasswordA1']
            PA2 = request.form['PasswordA2']
            USN = request.form['USN'].upper()
            Student = app.Student_Personal.query.filter_by(USN=USN).first()
            if P1 == P2:
                if Student.PasswordA1 == PA1 and Student.PasswordA2 == PA2:
                    Student.Password = bcrypt.hashpw(P1.encode('utf-8'), bcrypt.gensalt())
                    app.db.session.commit()
                    return redirect(url_for('Student.StudentLogin'))
                else:
                    flash("Check Answers again")
                    return render_template("StudentForgotPassword.html")
            else:
                flash("Both the password should same")
                return render_template("StudentForgotPassword.html", data=Student)
    return render_template("StudentForgotPassword.html")


@Students.route("/display/<id>", methods = ['POST', 'GET'])
@app.role_required("Student")
@login_required
def select(id):
    if id:
        Stu_Personal = app.Student_Personal.query.filter_by(USN = id).first()
        Stu_Family = app.Student_Family.query.filter_by(USN = id).first()
        Stu_Marks = app.Marks.query.filter_by(USN=id).all()
        Stu_Achievements = app.Achievements.query.filter_by(USN=id).all()
        Stu_Meeting = app.Meeting.query.filter_by(USN=id).all()
        if Stu_Personal and Stu_Family:
            image = b64encode(Stu_Personal.Image).decode("utf-8")
            return render_template("StudentViewProfile.html", data = Stu_Personal, image=image, data2 = Stu_Family, datamarks = Stu_Marks, datameetings = Stu_Meeting, dataachievements = Stu_Achievements)
        else:
            "No data found"
    flash("No data found")
    return redirect(url_for("Student.home"))

@Students.route("/viewcertificate/<id>", methods = ['POST', 'GET'])
@app.role_required("Student")
@login_required
def viewcertificate(id):
    certificate = app.Achievements.query.filter_by(_id=id).first()
    image = b64encode(certificate.Certificates).decode("utf-8")
    return render_template("Studentviewcertificate.html", image = image)