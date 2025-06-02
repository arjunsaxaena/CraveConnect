-----------------------------
-- Restaurant Management
-----------------------------
CREATE TABLE restaurants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    cuisine_types TEXT[] NOT NULL,
    rating NUMERIC(3,2) DEFAULT 0.00,
    delivery_radius_km NUMERIC(5,2) DEFAULT 5.00,
    min_order_amount NUMERIC(8,2) DEFAULT 0.00,
    delivery_fee NUMERIC(8,2) DEFAULT 0.00,
    operating_hours JSONB NOT NULL,
    location GEOGRAPHY(POINT,4326) NOT NULL,
    meta JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
