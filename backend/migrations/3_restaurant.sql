CREATE TABLE restaurants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    phone VARCHAR(15) UNIQUE,
    auth_provider TEXT CHECK (auth_provider IN ('google', 'phone')) NOT NULL,
    image_path TEXT,
    menu_path TEXT,
    meta JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
