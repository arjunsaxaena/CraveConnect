import enum

class FileTypes(enum.Enum):
    menu = 'menu'
    profile_image = 'profile_image'
    vehicle_image = 'vehicle_image'
    restaurant_logo = 'restaurant_logo'
    other = 'other'

class PaymentStatus(enum.Enum):
    initiated = 'initiated'
    success = 'success'
    failed = 'failed'
    refunded = 'refunded'

class VehicleType(enum.Enum):
    bike = 'bike'
    car = 'car'
    scooter = 'scooter'
    bicycle = 'bicycle'

class AuthProvider(enum.Enum):
    google = 'google'
    apple = 'apple'
    phone = 'phone' 

class SpiceTolerance(enum.Enum):
    low = 'low'
    medium = 'medium'
    high = 'high'
