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