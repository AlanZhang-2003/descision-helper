import random
import uuid
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, current_user, login_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///problem.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

STATUS = ["todo", "done"]
PRIORITY = [1,2,3,4,5]

class User(db.Model,UserMixin):
    id = db.Column(db.String, primary_key = True)
    username = db.Column(db.String(200), unique = True, nullable = False)
    password = db.Column(db.String(200), nullable = False)

class Problem(db.Model):
    id = db.Column(db.String, primary_key = True)
    title = db.Column(db.String(200), nullable = False)
    notes = db.Column(db.String(500))
    user_id = db.Column(db.String, db.ForeignKey("user.id"), nullable = False)
    options = db.relationship("Option", backref="problem", cascade="all, delete-orphan")

class Option(db.Model):
    id = db.Column(db.String, primary_key = True)
    problem_id = db.Column(db.String, db.ForeignKey("problem.id"))
    title = db.Column(db.String(200), nullable = False)
    notes = db.Column(db.String(500))
    priority = db.Column(db.Integer)
    status = db.Column(db.String(10))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route("/")
def home():
    return "Decision Helper is running!"

@app.route("/register", methods=["POST"])
def register():
    data = request.json

    user = User(
        id = str(uuid.uuid4()),
        username = data["username"],
        password = generate_password_hash(data["password"])
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"return": "registered account"})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(username=data["username"]).first()

    if not user:
        return jsonify({"return": "user not found"}), 404
    if not check_password_hash(user.password, data["password"]):
        return jsonify({"return": "wrong passwrod"}), 401

    login_user(user)
    return jsonify({"return": "logged in"})

#add problem
@app.route("/problem", methods=["POST"])
@login_required
def add_problem():
    data = request.json

    new_problem = Problem(
        id=str(uuid.uuid4()),
        title=data.get("title"),
        notes=data.get("notes"),
        user_id = current_user.id
    )

    db.session.add(new_problem)
    db.session.commit()

    return jsonify({
        "return": "Problem Added",
        "problem_id": new_problem.id,
    })

#remove problem
@app.route("/problem/<problem_id>", methods=["DELETE"])
@login_required
def delete_problem(problem_id):
    problem = Problem.query.filter_by(id=problem_id, user_id=current_user.id).first()

    if not problem:
        return jsonify({"error": "problem not found"}), 404

    db.session.delete(problem)
    db.session.commit()

    return jsonify({"return": "deleted problem"})

#update problem
@app.route("/problem/<problem_id>", methods=["PATCH"])
@login_required
def update_problem(problem_id):
    data = request.json
    
    problem = Problem.query.filter_by(id=problem_id, user_id=current_user.id).first()

    if not problem:
        return jsonify({"error": "no problem found"}), 404

    if "title" in data:
        problem.title = data["title"]
    
    if "notes" in data:
        problem.notes = data["notes"]

    db.session.commit()

    return jsonify({
        "return": "Problem Updated",
        "problem": {
            "id": problem.id,
            "title": problem.title,
            "notes": problem.notes
        }
    })

#list all problem
@app.route("/problem", methods=["GET"])
@login_required
def get_all_problems():
    db_problems = Problem.query.filter_by(user_id=current_user.id).all()
    
    result = []
    for p in db_problems:
        item = {
            "id" : p.id,
            "title" : p.title,
            "notes" : p.notes
        }
        result.append(item)
    return jsonify(result)

#add option
@app.route("/problem/<problem_id>/option", methods=["POST"])
@login_required
def add_options(problem_id):
    data = request.json
    problem = Problem.query.filter_by(id=problem_id, user_id=current_user.id).first()
    if not problem:
        return jsonify({"error": "no problem found"}), 404

    option = Option(
        id = str(uuid.uuid4()),
        problem_id = problem.id,
        title = data.get("title"),
        notes = data.get("notes"),
        priority = data.get("priority", 1),
        status = data.get("status", "todo")
    )

    db.session.add(option)
    db.session.commit()

    return jsonify({
        "return": "Option Added",
        "option": {
            "id": option.id,
            "title": option.title,
            "priority": option.priority,
            "status": option.status
        } 
    })

#Remove option
@app.route("/option/<option_id>", methods=["DELETE"])
@login_required
def delete_option(option_id):
    option = Option.query.join(Problem).filter(
        Option.id == option_id,
        Problem.user_id == current_user.id
    ).first()

    if not option:
        return jsonify({"error": "option not found"}), 404

    db.session.delete(option)
    db.session.commit()
    return jsonify({"return": "option deleted"})
    
#update option
@app.route("/option/<option_id>", methods=["PATCH"])
@login_required
def update_option(option_id):
    option = Option.query.join(Problem).filter(
        Option.id == option_id,
        Problem.user_id == current_user.id
    ).first()

    if not option :
        return jsonify({"error": "no option found"}), 404

    data = request.json

    if "title" in data:
        option.title = data["title"]

    if "notes" in data:
        option.notes = data["notes"]

    if "priority" in data:
        try:
            priority = int(data["priority"])
        except:
            return jsonify({"error": "priority must be a number"}), 400

        if priority not in PRIORITY:
            return jsonify({"error": "priority must be 1-5"}), 400

        option.priority = priority

    if "status" in data:
        if data["status"] not in STATUS:
            return jsonify({"error": "status must be done or todo"}),400

        option.status = data["status"]

    db.session.commit()
    
    return jsonify({
        "return": "Option Updated",
        "option": {
            "id": option.id,
            "title": option.title,
            "priority": option.priority,
            "status": option.status
        }
    })

#List options for problem
@app.route("/problem/<problem_id>/options", methods=["GET"])
@login_required
def get_options_from_problem(problem_id):
    db_options = fetch_options(problem_id)

    result = []
    for o in db_options:
        item = {
            "id": o.id,
            "problem_id": o.problem_id,
            "title": o.title,
            "notes": o.notes,
            "priority": o.priority,
            "status": o.status
        }
        result.append(item)

    return jsonify({"return": result})


#Decide function
def decide(option_list):
    if not option_list:
        return None

    highest_priority = max(option_list, key=lambda x: x["priority"] or 0)["priority"]

    top_options = [
        o for o in option_list
        if o["priority"] == highest_priority and o["status"] == "todo"
    ]
    if not top_options:
        return None

    return random.choice(top_options)

#decide an option for problem
@app.route("/decide/<problem_id>", methods=["GET"])
@login_required
def decide_route(problem_id):
    options = fetch_options(problem_id)
    result = []

    for o in options:
        item = {
            "id": o.id,
            "title": o.title,
            "notes": o.notes,
            "priority": o.priority,
            "status": o.status
        }
        result.append(item)

    chosen_option = decide(result)

    if chosen_option is None:
        return jsonify({"error": "No valid options"}), 400

    return jsonify(chosen_option)

#for testing
@app.route("/clean", methods=["POST"])
@login_required
def clean():
    Option.query.delete()
    Problem.query.delete()
    db.session.commit()
    return jsonify({"return": "clear db"})

@app.route("/clear/<problem_id>", methods=["POST"])
@login_required
def clear(problem_id):
    problem = Problem.query.filter_by(id=problem_id, user_id=current_user.id).first()
    for o in problem:
        db.sesssion.delete(o)
    db.session.delete(problem)
    db.session.commit()
    return jsonify({"return": "problem cleared"})

#option getter helper
def fetch_options(problem_id):
    problem = Problem.query.filter_by(
        id=problem_id,
        user_id=current_user.id
    ).first()

    if not problem:
        return []
    return Option.query.filter_by(problem_id=problem_id).all()


if __name__ == "__main__":
    app.run(debug=True)