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

@app.route("/options", methods=["POST"])
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

@app.rout("/options/<int:problem_id)", methods=["GET"])
def get_options_from_problem(problem_id):
    result = []
    for i in options:
        if i["problem_id"] == problem_id:
            result.append(i)
    return jsonify(result);

if __name__ == "__main__":
    app.run(debug=True)