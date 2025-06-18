from sqlalchemy.orm import Session
from typing import Any, Optional, TypeVar, Generic
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from app.core.errors import DatabaseIntegrityError, DatabaseOperationalError, DatabaseError

T = TypeVar('T')

class BaseRepository(Generic[T]):
    def __init__(self, model):
        self.model = model

    def get(self, db: Session, id: Any = None, filters: Optional[BaseModel] = None) -> Optional[T]:
        query = db.query(self.model)
        if id is not None:
            return query.get(id)
        if filters:
            for field, value in filters.dict(exclude_unset=True).items():
                if value is not None:
                    query = query.filter(getattr(self.model, field) == value)
            return query.all()
        return query.all()

    def create(self, db: Session, obj_in: Any) -> T:
        db_obj = self.model(**obj_in.dict())
        db.add(db_obj)
        try:
            db.commit()
            db.refresh(db_obj)
        except IntegrityError as e:
            db.rollback()
            raise DatabaseIntegrityError(str(e))
        except OperationalError as e:
            db.rollback()
            raise DatabaseOperationalError(str(e))
        except SQLAlchemyError as e:
            db.rollback()
            raise DatabaseError(str(e))
        return db_obj

    def update(self, db: Session, db_obj: T, obj_in: Any) -> T:
        obj_data = db_obj.__dict__
        update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        try:
            db.commit()
            db.refresh(db_obj)
        except IntegrityError as e:
            db.rollback()
            raise DatabaseIntegrityError(str(e))
        except OperationalError as e:
            db.rollback()
            raise DatabaseOperationalError(str(e))
        except SQLAlchemyError as e:
            db.rollback()
            raise DatabaseError(str(e))
        return db_obj

    def delete(self, db: Session, id: Any) -> Optional[T]:
        obj = db.query(self.model).get(id)
        if obj:
            db.delete(obj)
            try:
                db.commit()
            except IntegrityError as e:
                db.rollback()
                raise DatabaseIntegrityError(str(e))
            except OperationalError as e:
                db.rollback()
                raise DatabaseOperationalError(str(e))
            except SQLAlchemyError as e:
                db.rollback()
                raise DatabaseError(str(e))
        return obj
