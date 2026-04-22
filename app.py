import random
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import uuid

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///problem.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

STATUS = ["todo", "done"]
PRIORITY = [1,2,3,4,5]

class Problem(db.Model):
    id = db.Column(db.String, primary_key = True)
    title = db.Column(db.String(200), nullable = False)
    notes = db.Column(db.String(500))

class Option(db.Model):
    id = db.Column(db.String, primary_key = True)
    problem_id = db.Column(db.String, db.ForeignKey("problem.id"))
    title = db.Column(db.String(200), nullable = False)
    notes = db.Column(db.String(500))
    priority = db.Column(db.Integer)
    status = db.Column(db.String(10))

@app.route("/")
def home():
    return "Decision Helper is running!"

#add problem
@app.route("/problem", methods=["POST"])
def add_problem():
    data = request.json

    new_problem = Problem(
        id=str(uuid.uuid4()),
        title=data.get("title"),
        notes=data.get("notes")
    )

    db.session.add(new_problem)
    db.session.commit()

    return jsonify({
        "return": "Problem Added",
        "problem_id": new_problem.id,
    })

#remove problem
@app.route("/problem/<problem_id>", methods=["DELETE"])
def delete_problem(problem_id):
    problem = Problem.query.get(problem_id)

    if not problem:
        return jsonify({"error": "problem not found"}), 404

    related_options = Option.query.filter_by(problem_id=problem_id).all()
    
    for o in related_options:
        db.session.delete(o)

    db.session.delete(problem)
    db.session.commit()

    return jsonify({"return": "deleted problem"})

#update problem
@app.route("/problem/<problem_id>", methods=["PATCH"])
def update_problem(problem_id):
    data = request.json
    
    problem = Problem.query.get(problem_id)

    if not problem:
        return jsonify({"error": "no problem found"}), 404

    if "title" in data:
        problem.title = data["title"]
    
    if "notes" in data:
        problem.notes = data["notes"]
    
    if "priority" in data:
        problem.priority = data["priority"]
    
    if "status" in data:
        problem.status = data["status"]

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
def get_all_problems():
    db_problems = Problem.query.all()
    
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
def add_options(problem_id):
    data = request.json
    problem = Problem.query.get(problem_id)
    if not problem:
        return jsonify({"error": "no problem found"}), 404

    option = Option(
        id = str(uuid.uuid4()),
        problem_id = problem.id,
        title = data.get("title"),
        notes = data.get("notes"),
        priority = data.get("priority"),
        status = data.get("status")
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
def delete_option(option_id):
    option = Option.query.get(option_id)

    if not option:
        return jsonify({"error": "option not found"}), 404

    db.session.delete(option)
    db.session.commit()
    return jsonify({"return": "option deleted"})
    
#update option
@app.route("/option/<option_id>", methods=["PATCH"])
def update_option(option_id):
    data = request.json

    option = Option.query.get(option_id)

    if option == None:
        return jsonify({"error": "no option found"}), 404

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

    highest_priority = max(option_list, key=lambda x: x["priority"])["priority"]

    top_options = [
        o for o in option_list
        if o["priority"] == highest_priority and o["status"] == "todo"
    ]
    if not top_options:
        return None

    return random.choice(top_options)

#decide an option for problem
@app.route("/decide/<problem_id>", methods=["GET"])
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

@app.route("/clean", methods=["POST"])
def clean():
    Option.query.delete()
    Problem.query.delete()
    db.session.commit()
    return jsonify({"return": "clear db"})


#option getter helper
def fetch_options(problem_id):
    return Option.query.filter_by(problem_id=problem_id).all()


if __name__ == "__main__":
    app.run(debug=True)