from flask import  Blueprint, request, Response, abort, make_response
from .routes_utilities import validate_model, create_model, get_models_with_filters
from ..db import db
from app.models.goal import Goal
from app.models.task import Task


goals_bp = Blueprint("goals_bp", __name__, url_prefix = "/goals")

@goals_bp.get("")
def get_all_goals():
    # query = db.select(Goal)

    # sort_param = request.args.get("sort")
    # if sort_param == "desc":
    #     query = query.order_by(Goal.title.desc())
    
    # if sort_param == "asc":
    #     query = query.order_by(Goal.title)

    # goals = db.session.scalars(query)

    # goal_response = [goal.to_dict() for goal in goals]

    # return goal_response
    return get_models_with_filters(Goal, request.args)


@goals_bp.get("/<id>")
def get_one_Goal(id):
    goal = validate_model(Goal, id)
    return {"goal":goal.to_dict()}

@goals_bp.put("/<id>")
def update_Goal(id):
    goal = validate_model(Goal, id)
    request_body = request.get_json()

    goal.title = request_body["title"]

    db.session.commit()
    return Response(status=204, mimetype="application/json")


@goals_bp.delete("/<id>")
def delete_Goal(id):
    goal = validate_model(Goal, id)

    db.session.delete(goal)
    db.session.commit()

    return Response(status=204, mimetype="application/json")

@goals_bp.post("")
def post_new_Goal():
    request_body = request.get_json()
    
    # try: 
    #     new_goal = Goal.from_dict(request_body)
    # except KeyError as error:
    #     response = {"details": "Invalid data"}
    #     abort(make_response(response, 400))

    # db.session.add(new_goal)
    # db.session.commit()

    # return make_response({"goal": new_goal.to_dict()}, 201)
    return create_model(Goal, request_body)

@goals_bp.post("/<goal_id>/tasks")
def create_tasks_with_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    request_body = request.get_json()

    if not request_body or "task_ids" not in request_body:
        return make_response({"details": "Invalid data"}, 400)
    
    task_ids = request_body["task_ids"]

    goal.tasks.clear()
    
    for task_id in task_ids:
        task = validate_model(Task, task_id)
        task.goal_id = goal.id

    db.session.commit()

    return {"id": goal.id, "task_ids": task_ids}, 200


@goals_bp.get("/<goal_id>/tasks")
def get_tasks_by_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    response = {"id": goal.id, "title": goal.title, "tasks": [task.to_dict() for task in goal.tasks]}
    return response


    