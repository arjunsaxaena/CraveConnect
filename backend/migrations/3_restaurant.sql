CREATE TABLE restaurants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    email TEXT,
    phone VARCHAR(15),
    description TEXT,
    restaurant_image_ids UUID[] DEFAULT '{}',
    menu_image_ids UUID[] DEFAULT '{}',
    cuisine_type TEXT[],
    operating_hours JSONB DEFAULT '{}',
    location JSONB DEFAULT '{}',
    meta JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
