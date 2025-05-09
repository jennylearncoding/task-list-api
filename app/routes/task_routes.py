from flask import  Blueprint, request, Response, abort, make_response
from .routes_utilities import validate_model, create_model, get_models_with_filters
from ..db import db
from app.models.task import Task
from datetime import datetime
import os
import requests

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

    tasks_response = [task.to_dict() for task in tasks]

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
    return create_model(Task, request_body)

    # try: 
    #     new_task = Task.from_dict(request_body)
    # except KeyError as error:
    #     response = {"details": "Invalid data"}
    #     abort(make_response(response, 400))

    # db.session.add(new_task)
    # db.session.commit()

    # return make_response({"task": new_task.to_dict()}, 201)

def send_slack_msg(task_title):
    token = os.environ.get("SLACK_API_TOKEN")
    url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "channel": "task-notifications",
        "text": f"Someone just completed the task {task_title}"
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code != 200 or not response.json().get("ok"):
        print("Slack API error:", response.text)
