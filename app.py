from pys.user import user
from pys.admin import admin
from pys.authentication import authentication
from pymongo import MongoClient
from flask import Flask, redirect, url_for
import json

def insert(collection, document):
    match = collection.find_one(document)

    if not match:
        collection.insert_one(document)


def insert_json(path, collection):
    data = None

    try:
        with open(path, "r") as file:
            data = json.load(file)
    except Exception:
        print(f"Failed to read the file and/or parse json for the {collection} we want to insert to the database")
        return

    for document in data:
        insert(collection, document)


client = MongoClient("mongodb://mongodb:27017/")
db = client["DigitalNotes"]
notes = db["notes"]
users = db["users"]

app = Flask(__name__)
app.secret_key = "SECRET"


app.register_blueprint(authentication, url_prefix="/authentication")
app.register_blueprint(admin, url_prefix="/admin")
app.register_blueprint(user, url_prefix="/user")


@app.route("/home", methods=["GET"])
def index():
    return "<h1>Welcome to the Great Notes Website</h1>"


@app.route("/")
@app.route("/login")
@app.route("/signIn")
def routeToLogin():
    return redirect(url_for("authentication.signIn"))


if __name__ == "__main__":
    if not "GreatNotes" in db.list_collection_names():
        insert_json("notes.json", notes)
        insert_json("users.json", users)

    app.run(debug=True, host='0.0.0.0', port=5000)
