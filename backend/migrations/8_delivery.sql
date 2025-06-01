-----------------------------
-- Delivery Management
-----------------------------
CREATE TABLE delivery_partners (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    vehicle_type TEXT NOT NULL CHECK (
        vehicle_type IN ('bicycle', 'motorcycle', 'car', 'walking')
    ),
    vehicle_registration TEXT,
    current_location GEOGRAPHY(POINT,4326),
    is_available BOOLEAN DEFAULT TRUE,
    rating NUMERIC(3,2) DEFAULT 5.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE deliveries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID UNIQUE NOT NULL REFERENCES orders(id),
    partner_id UUID NOT NULL REFERENCES delivery_partners(id),
    pickup_time TIMESTAMP,
    delivery_route GEOGRAPHY(LINESTRING,4326),
    status TEXT CHECK (
        status IN (
            'assigned', 'picked_up', 'in_transit',
            'delivered', 'failed'
        )
    ) DEFAULT 'assigned',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);