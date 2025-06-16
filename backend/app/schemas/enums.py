from enum import Enum

class AuthProvider(str, Enum):
    google = "google"
    apple = "apple"
    phone = "phone"

class PaymentStatus(str, Enum):
    initiated = "initiated"
    success = "success"
    failed = "failed"
    refunded = "refunded"

class SpiceTolerance(str, Enum):
    low = "low"
    medium = "medium"
    high = "high" 