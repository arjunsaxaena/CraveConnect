from fastapi import HTTPException

class NotFoundError(HTTPException):
    def __init__(self, detail="Resource not found"):
        super().__init__(status_code=404, detail=detail)

class ConflictError(HTTPException):
    def __init__(self, detail="Conflict"):
        super().__init__(status_code=409, detail=detail) 