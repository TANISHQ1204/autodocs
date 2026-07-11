from flask import Flask

app = Flask(__name__)

@app.route("/users/<id>", methods=["GET"])
def get_user(id):
    return fetch_user_from_db(id)

@app.route("/users", methods=["POST"])
def create_user():
    return save_user_to_db()

@app.get("/health")
def health_check():
    return "ok"