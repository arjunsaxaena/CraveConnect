from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.order_assignments import OrderAssignmentCreate, OrderAssignmentUpdate, OrderAssignmentOut, OrderAssignmentListResponse, OrderAssignmentSingleResponse
from app.repositories.repository import OrderAssignmentsRepository, OrderRepository, DeliveryPersonRepository
from app.models.filters import GetOrderAssignmentsFilters
from app.models.order_assignments import OrderAssignments, validate_order_assignments
from app.core.errors import NotFoundError, BadRequestError
from app.core.responses import SuccessResponse, ErrorResponse

router = APIRouter(prefix="/order_assignments", tags=["order_assignments"])
order_assignment_repo = OrderAssignmentsRepository()
order_repo = OrderRepository()
delivery_person_repo = DeliveryPersonRepository()

@router.get("/", response_model=OrderAssignmentListResponse)
def get_order_assignments(filters: GetOrderAssignmentsFilters = Depends(), db: Session = Depends(get_db)):
    order_assignments = order_assignment_repo.get(db, filters=filters)
    if not order_assignments:
        raise NotFoundError("No order assignments found")
    return OrderAssignmentListResponse(data=order_assignments)

@router.post("/", response_model=OrderAssignmentSingleResponse, status_code=status.HTTP_201_CREATED)
def create_order_assignment(order_assignment: OrderAssignmentCreate, db: Session = Depends(get_db)):
    try:
        order_assignment_obj = OrderAssignments(**order_assignment.dict())
        validate_order_assignments(order_assignment_obj)

        order = order_repo.get(db, id=order_assignment.order_id)
        if not order:
            raise NotFoundError(f"Order {order_assignment.order_id} not found")

        delivery_person = delivery_person_repo.get(db, id=order_assignment.delivery_person_id)
        if not delivery_person:
            raise NotFoundError(f"Delivery person {order_assignment.delivery_person_id} not found")

        created = order_assignment_repo.create(db, obj_in=order_assignment)
        return OrderAssignmentSingleResponse(data=created, message="Order assignment created successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise BadRequestError(str(e))

@router.patch("/", response_model=OrderAssignmentSingleResponse, responses={404: {"model": ErrorResponse}, 400: {"model": ErrorResponse}})
def update_order_assignment(order_assignment_data: OrderAssignmentUpdate, order_assignment_id: str = Query(...), db: Session = Depends(get_db)):
    order_assignment = order_assignment_repo.get(db, id=order_assignment_id)
    if not order_assignment:
        raise NotFoundError(f"Order assignment {order_assignment_id} not found")

    if order_assignment_data.order_id:
        order = order_repo.get(db, id=order_assignment_data.order_id)
        if not order:
            raise NotFoundError(f"Order {order_assignment_data.order_id} not found")

    if order_assignment_data.delivery_person_id:
        delivery_person = delivery_person_repo.get(db, id=order_assignment_data.delivery_person_id)
        if not delivery_person:
            raise NotFoundError(f"Delivery person {order_assignment_data.delivery_person_id} not found")
    
    try:
        updated = order_assignment_repo.update(db, db_obj=order_assignment, obj_in=order_assignment_data)
        return OrderAssignmentSingleResponse(data=updated, message="Order assignment updated successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise BadRequestError(str(e))

@router.delete("/", response_model=SuccessResponse, responses={404: {"model": ErrorResponse}})
def delete_order_assignment(order_assignment_id: str, db: Session = Depends(get_db)):
    order_assignment = order_assignment_repo.get(db, id=order_assignment_id)
    if not order_assignment:
        raise NotFoundError(f"Order assignment {order_assignment_id} not found")
    order_assignment_repo.delete(db, id=order_assignment_id)
    return SuccessResponse(message="Order assignment deleted successfully")