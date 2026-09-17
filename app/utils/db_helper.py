from fastapi import HTTPException
from sqlalchemy.orm import Session


def get_or_404(db: Session, model, id_):
    obj = db.get(model, id_)
    if obj is None:
        raise HTTPException(status_code=404, detail=f"{model.__name__} {id_} not found")
    return obj


def save(db: Session, obj):
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def save_all(db: Session, *objs):
    db.add_all(objs)
    db.commit()
    for obj in objs:
        db.refresh(obj)
    return list(objs)
