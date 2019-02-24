from pymongo import MongoClient
from flask import Flask, jsonify, abort, make_response, request, url_for


app = Flask(__name__)
client = MongoClient('mongodb://localhost:27017')
db = client['test']
collection = db['todo_list']

tasks = []
cursor = collection.find()
for task in cursor:
    tasks.append(task)


# tasks = [
#     {
#         '_id': 1,
#         'title': u'Buy groceries',
#         'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
#         'done': False
#     },
#     {
#         '_id': 2,
#         'title': u'Learn Python',
#         'description': u'Need to find a good Python tutorial on the web',
#         'done': False
#     }
# ]


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


def make_public_task(task):
    new_task = {}
    for field in task:
        if field == '_id':
            new_task['uri'] = url_for('get_task', task_id=task['_id'], _external=True)
        else:
            new_task[field] = task[field]
    return new_task


@app.route("/")
def index():
    return '<h1>Welcome, Michael smart boy!</h1>'


@app.route("/todo/api/v1.0/tasks", methods=['GET'])
def get_tasks():
    return jsonify({'tasks': [make_public_task(t) for t in tasks]})


@app.route("/todo/api/v1.0/tasks/<int:task_id>", methods=['GET'])
def get_task(task_id):
    t = [task for task in tasks if task['_id'] == task_id]
    if len(t) == 0:
        abort(404)
    return jsonify({'task': t[0]})


@app.route("/todo/api/v1.0/tasks", methods=['POST'])
def create_task():
    if not request.json or not 'title' in request.json:
        abort(400)
    task = {
        '_id': 0 if len(tasks) == 0 else tasks[-1]['_id'] + 1,
        'description': request.json.get('description', ''),
        'done': False
    }
    tasks.append(task)
    collection.insert_one(task)
    return jsonify({'task': task}), 201


@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = [task for task in tasks if task['_id'] == task_id]
    if len(task) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'title' in request.json and type(request.json['title']) != str:
        abort(400)
    if 'description' in request.json and type(request.json['description']) is not str:
        abort(400)
    if 'done' in request.json and type(request.json['done']) is not bool:
        abort(400)
    task[0]['title'] = request.json.get('title', task[0]['title'])
    task[0]['description'] = request.json.get('description', task[0]['description'])
    task[0]['done'] = request.json.get('done', task[0]['done'])
    return jsonify({'task': task[0]})


@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = [task for task in tasks if task['_id'] == task_id]
    if len(task) == 0:
        abort(404)
    tasks.remove(task[0])
    return jsonify({'result': True})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
