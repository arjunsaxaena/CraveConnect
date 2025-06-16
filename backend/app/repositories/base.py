from sqlalchemy.orm import Session

class BaseRepository:
    def __init__(self, model):
        self.model = model

    def get(self, db: Session, id):
        return db.query(self.model).get(id)

    def create(self, db: Session, obj_in):
        db_obj = self.model(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    # Add update, delete, and other common methods as needed 