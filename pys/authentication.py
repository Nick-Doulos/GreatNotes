from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from pymongo import MongoClient

authentication = Blueprint("authentication", __name__, static_folder="static", template_folder="templates")

client = MongoClient("mongodb://mongodb:27017/")
db = client["DigitalNotes"]
notes = db["notes"]
users = db["users"]

@authentication.route("/signUp", methods=["GET", "POST"])
def signUp():
    if request.method == "GET":
        return render_template("signUp.html")
    else:
        userName = request.form["name"]
        userEmail = request.form["email"]
        userPassword = request.form["password"]

        userExists = users.find({"email": userEmail}).count()
        if userExists == 0:
            user = {"name": userName, "email": userEmail,
                    "password": userPassword, "category": "user"}
            users.insert_one(user)

            session["email"] = userEmail
            return redirect(url_for("authentication.userInformation"))
        else:
            flash(f"A user with this email already exists")
            return redirect(url_for("authentication.signUp"))


@authentication.route("/")
@authentication.route("/signIn", methods=["GET", "POST"])
def signIn():
    if request.method == "GET":
        return render_template("signIn.html")
    else:

        userEmail = request.form["email"]
        userPassword = request.form["password"]

        userExists = users.find_one({"email": userEmail})

        if userExists is None:
            flash("There is no user with this email")
            return redirect(url_for("authentication.signIn"))
        else:
            if userPassword == userExists["password"]:
                session["email"] = userEmail

                if userExists["category"] == "admin":
                    return render_template("changePass.html", email = userEmail)
                else:
                    return redirect(url_for("user.userHome"))
            else:
                return redirect(url_for("authentication.signIn"))


@authentication.route("/userInformation", methods=["GET"])
def userInformation():

    if "email" in session:
        theUser = users.find_one({"email": session["email"]})
        return render_template("user.html", usrName=theUser["name"], usrEmail=theUser["email"], usrCategory=theUser["category"])
    else:
        flash("You are not signed in to this website")
        return redirect(url_for("authentication.signIn"))
