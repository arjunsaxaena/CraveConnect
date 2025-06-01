-----------------------------
-- Restaurant Management
-----------------------------
CREATE TABLE restaurants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    cuisine_types TEXT[] NOT NULL,
    health_permit_number TEXT UNIQUE,
    rating NUMERIC(3,2) DEFAULT 0.00,
    delivery_radius_km NUMERIC(5,2) DEFAULT 5.00,
    min_order_amount NUMERIC(8,2) DEFAULT 0.00,
    delivery_fee NUMERIC(8,2) DEFAULT 0.00,
    preparation_time_min INT DEFAULT 30,
    operating_hours JSONB NOT NULL,
    location GEOGRAPHY(POINT,4326) NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE restaurant_images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    image_url TEXT NOT NULL,
    caption TEXT,
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);