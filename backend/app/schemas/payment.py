from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from datetime import datetime


class PaymentHistoryCreate(BaseModel):
    user_id: UUID
    items: List[str]
    prices: List[Decimal]
    razorpay_payment_id: Optional[str] = None
    razorpay_order_id: Optional[str] = None
    razorpay_signature: Optional[str] = None
    purchase_status: str = "PENDING"
    payment_method: Optional[str] = None
    totalAmount: Decimal
    payment_status: str = "PENDING"
    notes: Optional[dict] = None
    raw_payload: Optional[dict] = None


class PaymentHistoryUpdate(BaseModel):
    items: Optional[List[str]] = None
    prices: Optional[List[Decimal]] = None
    razorpay_payment_id: Optional[str] = None
    razorpay_order_id: Optional[str] = None
    razorpay_signature: Optional[str] = None
    purchase_status: Optional[str] = None
    payment_method: Optional[str] = None
    totalAmount: Optional[Decimal] = None
    payment_status: Optional[str] = None
    notes: Optional[dict] = None
    raw_payload: Optional[dict] = None


class PaymentHistoryOut(BaseModel):
    id: UUID
    user_id: UUID
    items: List[str]
    prices: List[Decimal]
    razorpay_payment_id: Optional[str] = None
    razorpay_order_id: Optional[str] = None
    razorpay_signature: Optional[str] = None
    purchased_at: datetime
    purchase_status: str
    payment_method: Optional[str] = None
    totalAmount: Decimal
    payment_status: str
    notes: Optional[dict] = None
    raw_payload: Optional[dict] = None
    payment_timestamp: Optional[datetime] = None


class RazorpayOrderCreate(BaseModel):
    amount: Decimal
    currency: str = "INR"
    receipt: Optional[str] = None
    notes: Optional[dict] = None


class RazorpayPaymentVerification(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


class PaymentResponse(BaseModel):
    success: bool
    payment_id: Optional[str] = None
    order_id: Optional[str] = None
    error_message: Optional[str] = None


# NEW: Response wrappers
class PaymentHistoryListResponse(BaseModel):
    data: List[PaymentHistoryOut]
    message: str = "Payment history fetched successfully"


class PaymentHistorySingleResponse(BaseModel):
    data: PaymentHistoryOut
    message: str = "Payment record fetched successfully"
