from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from pymongo import MongoClient

admin = Blueprint("admin", __name__, static_folder="static", template_folder="templates")

client = MongoClient("mongodb://mongodb:27017/")
db = client["DigitalNotes"]
notes = db["notes"]
users = db["users"]

admin.route("/")
@admin.route("/adminHome", methods=["GET"])
def adminHome():
    return render_template("admin.html", admEmail=session["email"])


admin.route("/changePass")
@admin.route("/changePass", methods=["GET", "POST"])
def changePass():
    if request.method == "GET":
        return render_template("changePass.html")
    else:
        adminEmail = request.form["email"]
        adminPassword = request.form["password"]
        Dict = users.find_one({"email": adminEmail})
        finalName = Dict["name"]

        users.delete_one({"email": adminEmail})

        user = {"name": finalName, "email": adminEmail, "password": adminPassword, "category": "admin"}
        users.insert_one(user)
        
        return redirect(url_for("admin.adminHome"))


@admin.route("/insert")
@admin.route("/insertAdmin", methods=["POST"])
def insertAdmin():
    if request.method == "POST":
        userName = request.form["name"]
        userEmail = request.form["email"]
        userPassword = request.form["password"]

    userExists = users.find({"email": userEmail}).count()
    if userExists == 0:
        user = {"name": userName, "email": userEmail, "password": userPassword, "category": "admin"}
        users.insert_one(user)
        session["email"] = userEmail
    else:
        flash(f"A admin with this email already exists")
    
    return redirect(url_for("admin.adminHome"))


@admin.route("/delete")
@admin.route("/deleteUser", methods=["POST"])
def deleteUser():
    if request.method == "POST":
        name = request.form["name"]
        userList = users.find({"name": name}).count()

        if userList == 0:
            flash(f"There is no user with this name")
        elif userList == 1:
            users.delete_one({"name": name})
            flash(f"You have successfully deleted the user: {name}")
        
        return redirect(url_for("admin.adminHome"))


@admin.route("/logout")
@admin.route("/logout", methods=["POST"])
def logout():
    if request.method == "POST":
        return redirect(url_for("authentication.signIn"))
