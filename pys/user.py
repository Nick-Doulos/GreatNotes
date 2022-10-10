import datetime
from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from pymongo import MongoClient
from itertools import chain
import re

user = Blueprint("user", __name__, static_folder="static",
                 template_folder="templates")

client = MongoClient("mongodb://mongodb:27017/")
db = client["DigitalNotes"]
notes = db["notes"]
users = db["users"]


@user.route("/")
@user.route("/userHome", methods=["GET"])
def userHome():
    return render_template("user.html", usrEmail=session["email"])


@user.route("/insert")
@user.route("/insertNote", methods=["POST"])
def insertNote():
    if request.method == "POST":
        title = request.form["title"]
        keys = request.form["keys"]
        note = request.form["note"]

        if notes.find_one({"title": title}):
            flash(f"The note with the title '{title}' already exists\nPlease insert one with a different title")
        else:
            created = datetime.datetime.now()
            canditateNote = {"title": title, "keywords": keys,
                              "note": note, "created": created}
            notes.insert_one(canditateNote)
            flash(
                f"The note with the title '{title}' has been inserted to the database")
        
        return redirect(url_for("user.userHome"))


@user.route("/search")
@user.route("/searchTitle", methods=["GET", "POST"])
def searchTitle():
    if request.method == "GET":
        return render_template("search.html")
    else:
        title = request.form["title"]
        result = notes.find({"title": title})

        if result.count() == 0:
            flash(f"There is no note with the title: {title}")
            return redirect(url_for("user.userHome"))
        else:
            return render_template("search.html", notes=result)


@user.route("/search")
@user.route("/searchKeyWord", methods=["GET", "POST"])
def searchKeyWord():
    if request.method == "GET":
        return render_template("search.html")
    else:
        result = None
        count = 0
        key = request.form["key"]
        notesList = notes.find()

        for i in notesList:
            keyword = i["keywords"]
            match = re.search(rf"\b{key}\b", keyword)
            if match and count == 0:
                result = notes.find({"keywords": keyword})
                count += 1
            elif match and count > 0:
                result = chain(result, notes.find({"keywords": keyword}))

        if result == None:
            flash(f"There is no note with the key: {key}")
            return redirect(url_for("user.userHome"))
        else:
            return render_template("search.html", notes=result)


@user.route("/update")
@user.route("/updateNote", methods=["POST"])
def updateNote():
    if request.method == "POST":
        title = request.form["title"]
        
        note = notes.find_one({"title": title})
        if note is None:
            flash("There is no note with the data inserted\nPlease try again")
            return redirect(url_for("user.userHome"))

        newTitle = request.form["newTitle"]
        newKeys = request.form["newKeys"]
        newNote = request.form["newNote"]

        if not newTitle:
            finalTitle = title
            Dict = notes.find_one({"title": title})
            finalKeys = Dict["keywords"]
            finalNote = Dict["note"]
        else:
            finalTitle = newTitle
            finalKeys = newKeys
            finalNote = newNote

        created = datetime.datetime.now()
        notes.update_one({"_id": note["_id"]}, {"$set": {"title": finalTitle, "keywords": finalKeys, "note": finalNote, "created": created}})
        flash("The note has been updated")
        return redirect(url_for("user.userHome"))


@user.route("/delete")
@user.route("/deleteNote", methods=["POST"])
def deleteNote():
    if request.method == "POST":
        title = request.form["title"]
        note = notes.find({"title": title}).count()

        if note == 0:
            flash(f"There is no note with this title")
            return redirect(url_for("user.userHome"))
        elif note == 1:
            notes.delete_one({"title": title})
            flash(f"You have successfully deleted the note: {title}")
            return redirect(url_for("user.userHome"))


@user.route("/chrono")
@user.route("/chrono", methods=["GET"])
def chrono():
    if request.method == "GET":
        note = notes.find().sort("created")
        return render_template("search.html", notes=note)


@user.route("/delete")
@user.route("/deleteAccount", methods=["POST"])
def deleteAccount():
    if request.method == "POST":
        email = session["email"]
        users.delete_one({"email": email})
        return redirect(url_for("authentication.signIn"))


@user.route("/logout")
@user.route("/logout", methods=["POST"])
def logout():
    if request.method == "POST":
        return redirect(url_for("authentication.signIn"))


@user.route("/back")
@user.route("/back", methods=["POST"])
def back():
    if request.method == "POST":
        return redirect(url_for("user.userHome"))
