from flask import  Blueprint, request, Response
from .routes_utilities import validate_model
from ..db import db
from app.models.task import Task
from datetime import datetime


tasks_bp = Blueprint("tasks_bp", __name__, url_prefix = "/tasks")

@tasks_bp.get("")
def get_all_tasks():
    query = db.select(Task)

    sort_param = request.args.get("sort")
    if sort_param == "desc":
        query = query.order_by(Task.title.desc())
    
    if sort_param == "asc":
        query = query.order_by(Task.title)

    tasks = db.session.scalars(query)

    tasks_response = []
    for task in tasks: 
        tasks_response.append(task.to_dict())

    return tasks_response

@tasks_bp.get("/<id>")
def get_one_task(id):
    task = validate_model(Task, id)
    return {"task":task.to_dict()}

@tasks_bp.put("/<id>")
def update_task(id):
    task = validate_model(Task, id)
    request_body = request.get_json()

    task.title = request_body["title"]
    task.description = request_body["description"]
    # if task.is_completed:
    #     task.complete_at = request_body["complete_at"]

    db.session.commit()
    return Response(status=204, mimetype="application/json")

@tasks_bp.patch("/<id>/mark_complete")
def is_completed(id):
    task = validate_model(Task, id)

    task.completed_at = datetime.now()

    db.session.commit()

    return Response(status=204, mimetype="application/json")

@tasks_bp.patch("/<id>/mark_incomplete")
def is_incompleted(id):
    task = validate_model(Task, id)

    task.completed_at = None

    db.session.commit()

    return Response(status=204, mimetype="application/json")


@tasks_bp.delete("/<id>")
def delete_task(id):
    task = validate_model(Task, id)

    db.session.delete(task)
    db.session.commit()

    return Response(status=204, mimetype="application/json")

@tasks_bp.post("")
def post_new_task():
    request_body = request.get_json()

    if not request_body.get("title") or not request_body.get("description"):
        return {"details":"Invalid data"}, 400

    new_task = Task.from_dict(request_body)

    db.session.add(new_task)
    db.session.commit()

    return {"task": new_task.to_dict()}, 201


    


