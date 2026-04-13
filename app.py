from asyncio.windows_events import NULL
import random
from flask import Flask, request, jsonify
import uuid

app = Flask(__name__)

#temporary database
problems = []
options = []

STATUS = ["todo", "done"]
PRIORITY = [1,2,3,4,5]

@app.route("/")
def home():
    return "Decision Helper is running!"

#add problem
@app.route("/problem", methods=["POST"])
def add_problem():
    data = request.json
    problems.append({
        "id": str(uuid.uuid4()),
        "title": data.get("title"),
        "notes": data.get("notes")
    })
    return jsonify({
        "return": "Problem Added",
        "problem": problems[-1]
    })

#remove problem
@app.route("/problem/<int:problem_id>", methods=["DELETE"])
def delete_problem(problem_id):
    for p in problems:
        if p["id"] == problem_id:
            problems.remove(p)
            return jsonify({"return": "Problem Deleted"})
    return jsonify({"error": "Problem not found"}), 404
    
#list all problem
@app.route("/problem", methods=["GET"])
def get_all_problems():
    return jsonify(problems)

#add option
@app.route("/option", methods=["POST"])
def add_options():
    data = request.json

    if not data.get("problem_id") or not data.get("title"):
        return jsonify({"error": "must have problem id and title"}), 400

    try:
        priority = int(data.get("priority"))
    except:
        return jsonify({"error:": "priority must be a number"}), 400

    if priority not in PRIORITY:
        return jsonify({"error": "Priority must be 1-5"}),400
    
    status = data.get("status", "todo")
    if data.get("status") not in STATUS:
        return jsonify({"error": "Status must be done or todo"}),400

    options.append({
        "id": str(uuid.uuid4()),
        "problem_id" : data.get("problem_id"),
        "title" : data.get("title"),
        "notes" : data.get("notes"),
        "priority" : priority,
        "status" : status
    })

    return jsonify({
        "return": "Option Added",
        "option": options[-1]
    })

#Remove option
@app.route("/option/<int:option_id>", methods=["DELETE"])
def delete_option(option_id):
    for o in options:
        if o["id"] == option_id:
            options.remove(o)
            return jsonify({"return": "Option Deleted"})
    return jsonify({"error": "Option not found"}), 404
    
#List options for problem
@app.route("/problems/<int:problem_id>/options", methods=["GET"])
def get_options_from_problem(problem_id):
    result = []
    for i in options:
        if i["problem_id"] == problem_id:
            result.append(i)
    return jsonify(result);

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

#Find options related to the problem (id)
def get_problem_options(problem_id):
    problem_options = []
    for o in options:
        if o["problem_id"] == problem_id:
            problem_options.append(o)
    return problem_options
    
#decide an option for problem
@app.route("/decide/<int:problem_id>")
def decide_route(problem_id):
    option_list = get_problem_options(problem_id)
    result = decide(option_list)

    if result is None:
        return jsonify({"error": "No valid options"}), 400

    return jsonify(result)

#update problem
@app.route("/problem/<int:problem_id>", methods=["PATCH"])
def update_problem(problem_id):
    data = request.json
    find_problem = None

    for p in problems:
        if p["id"] == problem_id:
            find_problem = p
            break

    if find_problem == None:
        return jsonify({"error": "no problem found"}), 404
    
    if "title" in data:
        find_problem["title"] = data["title"]
    
    if "notes" in data:
        find_problem["notes"] = data["notes"]

    return jsonify({
        "return": "Problem Updated",
        "problem": find_problem
    })

@app.route("/option/<int:option_id>", methods=["PATCH"])
def update_option(option_id):
    data = request.json

    find_option = None
    for o in options:
        if o["id"] == option_id:
            find_option = o
            break
    
    if find_option == None:
        return jsonify({"error": "no option found"}), 404

    if "title" in data:
        find_option["title"] == data["title"]

    if "notes" in data:
        find_option["notes"] == data["notes"]

    if "priority" in data:
        try:
            find_option["priority"] = int(data["priority"])
        except:
            return jsonify({"error": "priority must be a number"}), 400

        if find_option["priority"] not in PRIORITY:
            return jsonify({"error": "priority must be 1-5"}), 400
        
        find_option["priority"] == data["priority"]

    if "status" in data:
        if data["status"] not in STATUS:
            return jsonify({"error": "status must be done or todo"}),400

        find_option["status"] == data["status"]

    return jsonify({
        "return": "Option Updated",
        "option": find_option
    })



if __name__ == "__main__":
    app.run(debug=True)