from ..db import db
from flask import abort, make_response

def validate_model(cls, id):
    try: 
        id = int(id)
    except: 
        abort(make_response({"message": f"{cls.__name__} id {id} is invalid."}, 400))

    query = db.select(cls).where(cls.id == id)
    model = db.session.scalar(query)
    if not model:
        abort(make_response({"message": f"{cls.__name__} id {id} is not found."}, 404))
    return model

def create_model(cls, model_data):
    try:
        new_model = cls.from_dict(model_data)
    except KeyError as error:
        response = {"details": "Invalid data"}
        abort(make_response(response, 400))
    
    db.session.add(new_model)
    db.session.commit()

    return make_response({cls.__name__.lower(): new_model.to_dict()}, 201)
    


def get_models_with_filters(cls, filters=None):
    query = db.select(cls)

    if filters:
        for attribute, value in filters.items():
            if hasattr(cls, attribute):
                query = query.where(getattr(cls, attribute).ilike(f"%{value}%"))
    
    models = db.session.scalars(query.order_by(cls.id))
    models_response = [model.to_dict() for model in models]
    return models_response

