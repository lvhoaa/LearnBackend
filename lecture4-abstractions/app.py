import json

from db import db
from db import Category,Task,Subtask
from flask import Flask
from flask import request 

# define db filename
db_filename = "todo.db"
app = Flask(__name__)

# setup config
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_filename}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

# initialize app
db.init_app(app)
with app.app_context():
    db.create_all()


# generalized response formats
def success_response(data, code=200):
    return json.dumps(data), code
def failure_response(message, code=404):
    return json.dumps({"error": message}), code

# -- TASK ROUTES ------------------------------------------------------

@app.route("/")
@app.route("/tasks/")
def get_tasks():
    return success_response([t.serialize() for t in Task.query.all()])

@app.route('/subtasks/')
def get_subtasks():
    return success_response([sub.serialize() for sub in Subtask.query.all()])

@app.route('/categories/')
def get_categories():
    return success_response([c.serialize() for c in Category.query.all()])

@app.route("/tasks/", methods=["POST"])
def create_task():
    body = json.loads(request.data)
    new_task = Task(description = body.get('description'),done = body.get('done',False))
    db.session.add(new_task)
    db.session.commit()
    return success_response(new_task.serialize(),201)

@app.route("/tasks/<int:task_id>/")
def get_task(task_id):
    task = Task.query.filter_by(id=task_id).first()
    if task is None:
        return failure_response('Task not found')
    return success_response(task.serialize())

@app.route("/tasks/<int:task_id>/", methods=["POST"])
def update_task(task_id):
    task = Task.query.filter_by(id=task_id).first()
    if task is None:
        return failure_response('Task not found')
    body=json.loads(request.data)
    task.description=body.get('description',task.description)
    task.done = body.get('done',task.done)
    db.session.commit()
    return success_response(task.serialize())

@app.route("/tasks/<int:task_id>/", methods=["DELETE"])
def delete_task(task_id):
    task = Task.query.filter_by(id=task_id).first()
    if task is None:
        return failure_response('Task not found')
    db.session.delete(task)
    db.session.commit()
    return success_response(task.serialize())

# -- SUBTASK ROUTES ---------------------------------------------------

@app.route("/tasks/<int:task_id>/subtasks/", methods=["POST"])
def create_subtask(task_id):
    task = Task.query.filter_by(id=task_id).first()
    if task is None:
        return failure_response('Task not found')
    body = json.loads(request.data)
    new_subtask=Subtask(description=body.get('description'),done=body.get('done',False),task_id=task_id)
    db.session.add(new_subtask)
    db.session.commit()
    return success_response(new_subtask.serialize())
 
# -- CATEGORY ROUTES --------------------------------------------------

@app.route("/tasks/<int:task_id>/category/", methods=["POST"])
def assign_category(task_id):
    task = Task.query.filter_by(id=task_id).first()
    if task is None:
        return failure_response('Task not found')
    body = json.loads(request.data)
    description = body.get('description')
    if description is None:
        return failure_response('No desription')
    category = Category.query.filter_by(description=description).first()
    if category is None:
        new_category=Category(description=description,color=body.get('color','purple'))
    task.categories.append(new_category)
    db.session.commit()
    return success_response(task.serialize())
        
        

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
