from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File as FastAPIFile
from sqlalchemy.orm import Session
from app.repositories.repository import FileRepository, UserRepository, RestaurantRepository
from app.models.file import File, validate_file
from app.models.filters import GetFileFilters, GetRestaurantFilters
from app.core.responses import SuccessResponse, ErrorResponse
from app.db.session import get_db
from app.core.errors import NotFoundError, BadRequestError
from app.schemas.file import FileCreate, FileUpdate, FileListResponse, FileSingleResponse, FileCreateForm
from app.utils.file import save_file
from app.utils.ocr import process_menu_image
from app.models.enums import FileTypes

router = APIRouter(prefix="/files", tags=["files"])
file_repo = FileRepository()
user_repo = UserRepository()
restaurant_repo = RestaurantRepository()

@router.get("/", response_model=FileListResponse)
def get_files(filters: GetFileFilters = Depends(), db: Session = Depends(get_db)):
    files = file_repo.get(db, filters=filters)
    if not files:
        raise NotFoundError("No files found")
    return FileListResponse(data=files)

@router.post("/", response_model=FileSingleResponse, status_code=status.HTTP_201_CREATED)
def create_file(db: Session = Depends(get_db), file: UploadFile = FastAPIFile(...), form_data: FileCreateForm = Depends()):
    try:
        file_path = save_file(file)

        file_data = FileCreate(
            file_url=file_path,
            file_type=form_data.file_type,
            uploaded_by=form_data.uploaded_by,
            meta=form_data.meta
        )
        file_obj = File(**file_data.dict())
        validate_file(file_obj)

        user = user_repo.get(db, id=file_data.uploaded_by)
        if not user:
            raise NotFoundError(f"User {file_data.uploaded_by} not found")

        restaurant = None
        if form_data.file_type == FileTypes.MENU or form_data.file_type == FileTypes.RESTAURANT_LOGO:
            restaurant_filter = GetRestaurantFilters(owner_id=file_data.uploaded_by)
            restaurants = restaurant_repo.get(db, filters=restaurant_filter)
            if not restaurants:
                raise NotFoundError(f"Restaurant for user {file_data.uploaded_by} not found")
            restaurant = restaurants[0]

        created = file_repo.create(db, obj_in=file_data)

        if form_data.file_type == FileTypes.MENU and restaurant and restaurant.id:
            process_menu_image(db=db, file_path=file_path, restaurant_id=restaurant.id)

        return FileSingleResponse(data=created, message="File created successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise BadRequestError(str(e))

@router.patch("/", response_model=FileSingleResponse, responses={404: {"model": ErrorResponse}, 400: {"model": ErrorResponse}})
def update_file(file_data: FileUpdate, file_id: str = Query(...), db: Session = Depends(get_db)):
    file = file_repo.get(db, id=file_id)
    if not file:
        raise NotFoundError(f"File {file_id} not found")
    try:
        updated = file_repo.update(db, db_obj=file, obj_in=file_data)
        return FileSingleResponse(data=updated, message="File updated successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise BadRequestError(str(e))

@router.delete("/{file_id}", response_model=SuccessResponse, responses={404: {"model": ErrorResponse}})
def delete_file(file_id: str, db: Session = Depends(get_db)):
    file = file_repo.get(db, id=file_id)
    if not file:
        raise NotFoundError(f"File {file_id} not found")
    file_repo.delete(db, db_obj=file)
    return SuccessResponse(message="File deleted successfully")
