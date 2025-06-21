from enum import Enum

class FileTypes(str, Enum):
    MENU = "menu"
    PROFILE_IMAGE = "profile_image"
    VEHICLE_IMAGE = "vehicle_image"
    RESTAURANT_LOGO = "restaurant_logo"
    OTHER = "other"

class AuthProvider(str, Enum):
    GOOGLE = "google.com"
    APPLE = "apple"
    PHONE = "phone"

class VehicleType(str, Enum):
    BIKE = "bike"
    CAR = "car"
    SCOOTER = "scooter"
    BICYCLE = "bicycle"

class PaymentStatus(str, Enum):
    INITIATED = "initiated"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"

class SpiceTolerance(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
