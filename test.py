import requests

# 1. Create a problem
r1 = requests.post("http://127.0.0.1:5000/problem", json={
    "title": "What should I study?"
})
print("Problem:", r1.json())

# get problem id from response (safer than assuming 1)
problem_id = r1.json()["problem"]["id"]

# 2. Add options (FIXED ROUTE + FIELD NAMES)
r2 = requests.post("http://127.0.0.1:5000/option", json={
    "problem_id": problem_id,
    "title": "Study Python",
    "priority": 5,
    "notes": "focus basics",
    "status": "todo"
})
print("Option 1:", r2.json())

r3 = requests.post("http://127.0.0.1:5000/option", json={
    "problem_id": problem_id,
    "title": "Study SQL",
    "priority": 5,
    "notes": "databases",
    "status": "todo"
})
print("Option 2:", r3.json())

r4 = requests.post("http://127.0.0.1:5000/option", json={
    "problem_id": problem_id,
    "title": "LeetCode",
    "priority": 5,
    "notes": "Learning interview quesiton",
    "status": "todo"
})
print("Option 3:", r4.json())

# 3. Verify options
r5 = requests.get(f"http://127.0.0.1:5000/option/{problem_id}")
print("All options:", r5.json())