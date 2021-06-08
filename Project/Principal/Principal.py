import Proctor_Board.Project.app as app

from flask import Blueprint, render_template, request, json
from base64 import b64encode

Principals = Blueprint('Principal', __name__, template_folder="templates", static_folder="static")

@Principals.route("/")
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