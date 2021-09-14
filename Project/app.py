import os
import bcrypt
import pandas as pd

from flask import Flask, render_template, redirect, url_for, flash, session, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField
from flask_bootstrap import Bootstrap
from wtforms.validators import InputRequired
from flask_login import LoginManager, UserMixin, logout_user, current_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from functools import wraps
from flask_abort import abort
from flask_socketio import SocketIO
from wtforms import StringField, SelectField, PasswordField
from wtforms.validators import InputRequired, EqualTo, length

try:
    from Proctor.Proctor import Proctors
    from Student.Student import Students
    from Principal.Principal import Principals
    from ChiefProctor.ChiefProctor import ChiefProctors
except:
    pass

basedir = os.path.abspath(os.path.dirname(__file__))




#app_definitions
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'Proctor_Board.sqlite3')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "Kcube"


#global_variables
Courses = {'BCA': 'bca', 'BSC' : 'bsc', 'BCOM' : 'Bcom'}
Semester = {'1':'First', '2':'Second', '3':'Third', '4':'Fourth', '5':'Fifth', '6':'Sixth'}
Password_Recover_Questions = {'Choose Question':'Choose Question','What is the name of your first pet?':'What is the name of your first pet?', 'Which is your favourite car?':'Which is your favourite car?', 'What was your childhood nickname?':'What was your childhood nickname?', 'What is the name of your favorite childhood friend?':'What is the name of your favorite childhood friend?', 'What school did you attend for sixth grade?':'What school did you attend for sixth grade?'}
Blood_Group = {'A-Positive':'A+', 'A-Negative':'A-', 'B-Positive':'B+', 'B-Negative':'B-', 'AB-Positive':'AB+', 'AB-Negative':'AB-', 'O-Positive':'O+', 'O-Negative':'O-', 'NA':'Not Known'}
EventType = {'Co-Curricular':'Co-Curricular','Cultural':'Cultural','Seminar / Paper Presentation':'Seminar/Paper-Presentation','Sports':'Sports'}
Users = {'ChiefProctor':'ChiefProctor','Principal':'Principal'}
Allowed_Extensions = set(['png','jpg','jpeg'])

#declaring_Subjects
Columns = ['1','2','3','4','5','6']
Rows = ['BCA','BCOM','Bsc']
# arrays = [[['BCA11','BCA12','BCA13'],['BCA21','BCA22','BCA23'],['BCA31','BCA32','BCA33']],
#          [['Bcom11','Bcom12','Bcom13'],['Bcom21','Bcom22','Bcom23'],['Bcom31','Bcom32','Bcom33']],
#          [['Bsc11','Bsc12','Bsc13'],['Bsc21','Bsc22','Bsc23'],['Bsc31','Bsc32','Bsc33']]]
# panda_df = pd.DataFrame(data = arrays, index = Rows, columns = Columns)

arrays = [[['BCA11','BCA12','BCA13'],['BCA21','BCA22','BCA23'],['BCA31','BCA32','BCA33'],['BCA41','BCA42','BCA43'],['BCA51','BCA52','BCA53'],['BCA61','BCA62','BCA63']],
         [['Bcom11','Bcom12','Bcom13'],['Bcom21','Bcom22','Bcom23'],['Bcom31','Bcom32','Bcom33'],['Bcom41','Bcom42','Bcom43'],['Bcom51','Bcom52','Bcom53'],['Bcom61','Bcom62','Bcom63']],
         [['Bsc11','Bsc12','Bsc13'],['Bsc21','Bsc22','Bsc23'],['Bsc31','Bsc32','Bsc33'],['Bsc41','Bsc42','Bsc43'],['Bsc51','Bsc52','Bsc53'],['Bsc61','Bsc62','Bsc63']]]

panda_df = pd.DataFrame(data = arrays, index = Rows, columns = Columns)

print(panda_df['1']['BCA'])

#included_modules
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
socketio = SocketIO(app)


#To_logout_when_disconnected
@socketio.on('disconnect')
def disconnect_user():
    logout_user()
    session.pop('yourkey', None)

#Required_Global_Variables
Usertype = ""


#DB Tables
#Announcements
class Announcement(db.Model):
    __tablename__ = 'Announcement'
    _id = db.Column("id", db.Integer, primary_key = True)
    Date = db.Column(db.String(20))
    Announcement = db.Column(db.String(100))
    Status = db.Column(db.String(30))

    def __init__(self, Date, Announcement, Status):
        self.Date = Date
        self.Announcement = Announcement
        self.Status = Status


#Meeting
class Meeting(db.Model):
    __tablename__ = 'Meeting'
    _id = db.Column("id", db.Integer, primary_key=True)
    Name = db.Column(db.String(50))
    USN = db.Column(db.String(20))
    _class = db.Column(db.String(50))
    Semester = db.Column(db.String(10))
    ExamType = db.Column(db.String(30))
    Achievements_Difficulties = db.Column(db.String(100))
    GoalSetting = db.Column(db.String(100))
    Workplan = db.Column(db.String(100))
    DateTime = db.Column(db.String(30))

    def __init__(self, Name, USN, _class, Semester, Examtype, Achievements_Difficulties, GoalSetting, Workplan, DateTime):
        self.Name = Name
        self.USN = USN
        self._class = _class
        self.Semester = Semester
        self.ExamType = Examtype
        self.Achievements_Difficulties = Achievements_Difficulties
        self.GoalSetting = GoalSetting
        self.Workplan = Workplan
        self.DateTime = DateTime


#Student_Marks
class Marks(db.Model):
    __tablename__ = 'Marks'
    _id = db.Column("id", db.Integer, primary_key=True)
    Name = db.Column(db.String(50))
    USN = db.Column(db.String(20))
    _class = db.Column(db.String(50))
    Semester = db.Column(db.String(10))
    Subject = db.Column(db.String(30))
    Marks = db.Column(db.Integer)
    Remarks = db.Column(db.String(50))

    def __init__(self, Name, USN, _class, Semester, Subject, Marks, Remarks):
        self.Name = Name
        self.USN = USN
        self._class = _class
        self.Semester = Semester
        self.Subject = Subject
        self.Marks = Marks
        self.Remarks = Remarks


#Proctor_Details
class Proctor(UserMixin, db.Model):
    __tablename__ = 'Proctor'
    _id = db.Column("id", db.Integer, primary_key = True)
    Name = db.Column(db.String(50))
    EmployeeID = db.Column(db.String(50), unique=True)
    Department = db.Column(db.String(50))
    Mobile = db.Column(db.String(50))
    BloodGroup = db.Column(db.String(20))
    Password = db.Column(db.String(50))
    PasswordQ1 = db.Column(db.String(100))
    PasswordA1 = db.Column(db.String(50))
    PasswordQ2 = db.Column(db.String(100))
    PasswordA2 = db.Column(db.String(50))
    RemovalMessage = db.Column(db.String(100))
    RoleID = db.Column(db.String(20))
    Status = db.Column(db.String(20))

    def __init__(self, Name, EmployeeID, Department, Mobile, BloodGroup, Password, PasswordQ1, PasswordA1, PasswordQ2, PasswordA2, RemovalMessage, RoleID, Status):
        self.Name = Name
        self.EmployeeID = EmployeeID
        self.Department = Department
        self.Mobile = Mobile
        self.BloodGroup = BloodGroup
        self.Password = Password
        self.PasswordQ1 = PasswordQ1
        self.PasswordA1 = PasswordA1
        self.PasswordQ2 = PasswordQ2
        self.PasswordA2 = PasswordA2
        self.RemovalMessage = RemovalMessage
        self.RoleID = RoleID
        self.Status = Status

    def get_id(self):
        return (self._id)

    def get_role(self):
        return (self.RoleID)

#Student_Personal
class Student_Personal(UserMixin, db.Model):
    __tablename__ = 'Student_Personal'
    _id = db.Column("id", db.Integer, primary_key=True)
    Name = db.Column(db.String(30))
    USN = db.Column(db.String(20), unique=True)
    ProgramEnrolled = db.Column(db.String(30))
    Year = db.Column(db.String(10))
    Semester = db.Column(db.Integer)
    Gender = db.Column(db.String(10))
    Mobile = db.Column(db.String(15))
    DOB = db.Column(db.Date)
    BloodGroup = db.Column(db.String(10))
    Email = db.Column(db.String(20))
    Address = db.Column(db.String(100))
    City = db.Column(db.String(20))
    State = db.Column(db.String(20))
    Zipcode = db.Column(db.String(10))
    Hobbies = db.Column(db.String(30))
    Proctor = db.Column(db.String(20))
    ProctorID = db.Column(db.String(20))
    Password = db.Column(db.String(20))
    PasswordQ1 = db.Column(db.String(30))
    PasswordA1 = db.Column(db.String(30))
    PasswordQ2 = db.Column(db.String(30))
    PasswordA2 = db.Column(db.String(30))
    Image = db.Column(db.Text)
    Image_mime = db.Column(db.Text)
    Image_Filename = db.Column(db.Text)
    Status = db.Column(db.String(10))
    RemoveMsg = db.Column(db.String(30))
    RoleID = db.Column(db.String(20))

    def __init__(self, Name, USN, ProgramEnrolled, Year, Semester, Gender, Mobile, DOB, BloodGroup, Email, Address, City, State, Zipcode, Hobbies, Proctor, ProctorID, Password, PasswordQ1, PasswordA1, PasswordQ2, PasswordA2, Image, Image_mime, Image_Filename, Status, RemoveMsg, RoleID):
        self.Name = Name
        self.USN = USN
        self.ProgramEnrolled = ProgramEnrolled
        self.Year = Year
        self.Semester = Semester
        self.Gender = Gender
        self.Mobile = Mobile
        self.DOB = DOB
        self.BloodGroup = BloodGroup
        self.Email = Email
        self.Address = Address
        self.City = City
        self.State = State
        self.Zipcode = Zipcode
        self.Hobbies = Hobbies
        self.Proctor = Proctor
        self.ProctorID = ProctorID
        self.Password = Password
        self.PasswordQ1 = PasswordQ1
        self.PasswordA1 = PasswordA1
        self.PasswordQ2 = PasswordQ2
        self.PasswordA2 = PasswordA2
        self.Image = Image
        self.Image_mime = Image_mime
        self.Image_Filename = Image_Filename
        self.Status = Status
        self.RemoveMsg = RemoveMsg
        self.RoleID = RoleID

    def get_id(self):
        return (self._id)
    
    def get_role(self):
        return (self.RoleID)

#Student_Family
class Student_Family(db.Model):
    __tablename__ = 'Student_Family'
    _id = db.Column("id", db.Integer, primary_key=True)
    Name = db.Column(db.String(30))
    USN = db.Column(db.String(20), unique=True)
    Father_Name = db.Column(db.String(30))
    Father_Qualification = db.Column(db.String(30))
    Father_Profession = db.Column(db.String(30))
    Mother_Name = db.Column(db.String(30))
    Mother_Qualification = db.Column(db.String(30))
    Mother_Profession = db.Column(db.String(30))
    Sibling1_Name = db.Column(db.String(30))
    Sibling1_Qualification = db.Column(db.String(30))
    Sibling1_Profession = db.Column(db.String(30))
    Sibling2_Name = db.Column(db.String(30))
    Sibling2_Qualification = db.Column(db.String(30))
    Sibling2_Profession = db.Column(db.String(30))
    SSLC_Institute = db.Column(db.String(30))
    SSLC_Year = db.Column(db.String(30))
    SSLC_Percentage = db.Column(db.Float)
    PUC_Institute = db.Column(db.String(30))
    PUC_Year = db.Column(db.String(30))
    PUC_Percentage = db.Column(db.Float)
    Part_Time_Jobs = db.Column(db.String(30))
    Future_Plans = db.Column(db.String(30))

    def __init__(self, Name, USN, Father_Name, Father_Qualification, Father_Profession, Mother_Name, Mother_Qualification, Mother_Profession, Sibling1_Name, Sibling1_Qualification, Sibling1_Profession, Sibling2_Name, Sibling2_Qualification, Sibling2_Profession, SSLC_Institute, SSLC_Year, SSLC_Percentage, PUC_Institute, PUC_Year, PUC_Percentage, Part_Time_Jobs, Future_Plans):
        self.Name = Name
        self.USN = USN
        self.Father_Name = Father_Name
        self.Father_Qualification = Father_Qualification
        self.Father_Profession = Father_Profession
        self.Mother_Name = Mother_Name
        self.Mother_Qualification = Mother_Qualification
        self.Mother_Profession = Mother_Profession
        self.Sibling1_Name = Sibling1_Name
        self.Sibling1_Qualification = Sibling1_Qualification
        self.Sibling1_Profession = Sibling1_Profession
        self.Sibling2_Name = Sibling2_Name
        self.Sibling2_Qualification = Sibling2_Qualification
        self.Sibling2_Profession = Sibling2_Profession
        self.SSLC_Institute = SSLC_Institute
        self.SSLC_Year = SSLC_Year
        self.SSLC_Percentage = SSLC_Percentage
        self.PUC_Institute = PUC_Institute
        self.PUC_Year = PUC_Year
        self.PUC_Percentage = PUC_Percentage
        self.Part_Time_Jobs = Part_Time_Jobs
        self.Future_Plans = Future_Plans


#Feedback_table
class Feedback(db.Model):
    __tablename__ = 'Feedback'
    _id = db.Column("id", db.Integer, primary_key=True)
    Name = db.Column(db.String(255))
    Designation = db.Column(db.String(255))
    Feedback = db.Column(db.String(255))

    def __init__(self, Name, Designation, Feedback):
        self.Name = Name
        self.Designation = Designation
        self.Feedback = Feedback

#Achievements_table
class Achievements(db.Model):
    __tablename__ = 'Achievements'
    _id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(50))
    USN = db.Column(db.String(50))
    EventType = db.Column(db.String(50))
    EventName = db.Column(db.String(50))
    PrizesWon = db.Column(db.String(50))
    Certificates = db.Column(db.Text)
    Certificates_Filename = db.Column(db.Text)
    Certificates_Mimetype = db.Column(db.Text)

    def __init__(self, Name, USN, EventType, EventName, PrizesWon, Certificates, Certificates_FileName, Certificates_Mimetype):
        self.Name = Name
        self.USN = USN
        self.EventType = EventType
        self.EventName = EventName
        self.PrizesWon = PrizesWon
        self.Certificates = Certificates
        self.Certificates_Filename = Certificates_FileName
        self.Certificates_Mimetype = Certificates_Mimetype


#admin-Credentials
admin = Admin(app)
admin.add_view(ModelView(Student_Personal, db.session))
admin.add_view(ModelView(Student_Family, db.session))
admin.add_view(ModelView(Feedback, db.session))


#Decorators
def role_required(roles):
    def decorator(f):
        @wraps(f)
        def roles_required(*args, **kwargs):
            if current_user:
                if not current_user.RoleID == roles:
                    #print("Working in wraps")
                    #flash("You do not have permission to access this page", "warning")
                    abort(404, "You don't have permission to access this page ")
                return f(*args, **kwargs)
            else:
                #print("Working in wraps")
                #flash("You do not have permission to access this page", "warning")
                abort(404)
        return roles_required
    return decorator
            

#Forms
#Feedback_Form
class FeedbackForm(FlaskForm):
    Name = StringField('Name',[InputRequired()])
    Designation = SelectField(choices=Courses)
    Feedback = TextAreaField('Feedback',[InputRequired()])

#PRoctor_Details
class ProctorRegistrationForm(FlaskForm):
    Name = StringField('Name', validators=[InputRequired(message='Required'), length(min=3, max=30, message="Name should be below 30 Characters")])
    EmployeeID = StringField('EmployeeID', validators=[InputRequired(message='Required'), length(min=3, max=30, message="EmployeeID should be below 30 Characters")])
    Department = SelectField(choices=Courses)
    Mobile = StringField(validators=[InputRequired(message="Mobile Number Required")])
    BloodGroup = SelectField(choices=Blood_Group)
    Password = PasswordField('Password', validators=[InputRequired(message='Required')])
    Confirm_Password = StringField(validators=[InputRequired(message='Required'), EqualTo('Password', message="Both the password should same")])
    PasswordQ1 = SelectField(choices=Password_Recover_Questions)
    PasswordA1 = StringField(validators=[InputRequired(message="Mobile Number Required")])
    PasswordQ2 = SelectField(choices=Password_Recover_Questions)
    PasswordA2 = StringField(validators=[InputRequired(message="Mobile Number Required")])
    Usertype = SelectField(choices=Users)


@login_manager.user_loader
def load_user(user_id):
    if session['Usertype'] == "Student":
        return Student_Personal.query.filter_by(_id=user_id).first()
    elif session['Usertype'] == "Proctor":
        return Proctor.query.filter_by(_id=user_id).first()
    elif session['Usertype'] == "ChiefProctor":
        return Proctor.query.filter_by(_id=user_id).first()
    elif session['Usertype'] == "Principal":
        return Proctor.query.filter_by(_id=user_id).first()


#routes
#route_Home
@app.route("/home")
@app.route("/")
def home():
    Announcements = Announcement.query.all()
    logout_user()
    return render_template("index.html", data = Announcements)


#route_AboutUs
@app.route("/ren_aboutus")
def aboutus():
    return render_template("aboutus.html")


#route_Render_Feedback
@app.route("/ren_feedback", methods=['GET', 'POST'])
def feedback():
    feedbackform = FeedbackForm()
    if feedbackform.validate_on_submit():
        Name = feedbackform.Name.data
        Designation = feedbackform.Designation.data
        Message = feedbackform.Feedback.data
        data = Feedback(Name, Designation, Message)
        db.session.add(data)
        db.session.commit()
        flash("Thank you for feedback")
        return redirect(url_for('feedback'))
    return render_template("feedback.html", form=feedbackform)


#route_Render_ContactUs
@app.route("/ren_contactus")
def contactus():
    return render_template("contactus.html")

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/defaultlogin", methods=['GET', 'POST'])
def deflogin():
    if request.method == "POST":
        if request.form["Name"] == "Admin" and request.form["password"] == "Admin@123#":
            return redirect(url_for("defaulthome"))
        else:
            return "<p>This page is only for Admins. <a href='/'>Go to home</a></p>"
    return render_template("defaultlogin.html")

@app.route("/defaulthome", methods=['GET','POST'])
def defaulthome():
    defhomeform = ProctorRegistrationForm(request.form)
    if request.method == "POST":
        if defhomeform.validate_on_submit():
            Name = defhomeform.Name.data
            EmployeeID = defhomeform.EmployeeID.data.upper()
            Department = defhomeform.Department.data
            Mobile = defhomeform.Mobile.data
            BloodGroup = defhomeform.BloodGroup.data
            Password = bcrypt.hashpw(defhomeform.Password.data.encode('utf-8'), bcrypt.gensalt())
            PasswordQ1 = defhomeform.PasswordQ1.data
            PasswordA1 = defhomeform.PasswordA1.data
            PasswordQ2 = defhomeform.PasswordQ2.data
            PasswordA2 = defhomeform.PasswordA2.data
            Usertype = defhomeform.Usertype.data
            proctor = Proctor.query.filter_by(EmployeeID=EmployeeID).first()

            if proctor:
                flash("User Already exist try login")
                return redirect(url_for('defaulthome'))

            else:
                new_proctor = Proctor(Name, EmployeeID, Department, Mobile, BloodGroup, Password, PasswordQ1,PasswordA1, PasswordQ2, PasswordA2, '', Usertype, 'Active')
                db.session.add(new_proctor)
                db.session.commit()
                flash("User Added")
                return redirect(url_for('home'))
    return render_template("defaulthome.html", form = defhomeform)

#Main_Definition
if __name__ == "__main__":
    db.create_all()
    app.register_blueprint(Students, url_prefix="/Student")
    app.register_blueprint(Proctors, url_prefix="/Proctor")
    app.register_blueprint(Principals, url_prefix="/Principal")
    app.register_blueprint(ChiefProctors, url_prefix="/ChiefProctor")
    app.run(debug=True)

