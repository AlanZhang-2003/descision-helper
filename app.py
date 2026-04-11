import random
from flask import Flask, request, jsonify

app = Flask(__name__)

#temporary database
problems = []
options = []

@app.route("/")
def home():
    return "Decision Helper is running!"

@app.route("/problem", methods=["POST"])
def add_problem():
    data = request.json
    problems.append({
        "id": len(problems) + 1,
        "title": data.get("title"),
        "notes": data.get("notes")
    })
    return jsonify({
        "return": "Problem Added",
        "problem": problems[-1]
    })

@app.route("/problem", methods=["GET"])
def get_all_problems():
    return jsonify(problems)

@app.route("/option", methods=["POST"])
def add_options():
    data = request.json
    options.append({
        "id": len(options) + 1,
        "problem_id" : data.get("problem_id"),
        "title" : data.get("title"),
        "notes" : data.get("notes"),
        "priority" : data.get("priority"),
        "status" : data.get("status")
    })

    return jsonify({
        "return": "Option Added",
        "option": options[-1]
    })

@app.route("/option/<int:problem_id>", methods=["GET"])
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
def get_options_from_problem(problem_id):
    problem_options = []
    for o in options:
        if o["problem_id"] == problem_id:
            problem_options.append(o)
    return problem_options
    
#decide an option for problem
@app.route("/decide/<int:problem_id>")
def decide_route(problem_id):
    option_list = get_options_from_problem(problem_id)
    result = decide(option_list)

    if result is None:
        return jsonify({"error": "No valid options"}), 400

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)