-----------------------------
-- Core User Management
-----------------------------
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION postgis;

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone VARCHAR(15) UNIQUE NOT NULL,
    auth_provider TEXT CHECK (auth_provider IN ('google', 'phone')) NOT NULL,
    preference_tags TEXT[], -- For AI recommendations
    dietary_restrictions TEXT[],
    default_address_id UUID,
    meta JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_addresses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    address_line1 TEXT NOT NULL,
    address_line2 TEXT,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    postal_code TEXT NOT NULL,
    country TEXT NOT NULL,
    alias_name TEXT,
    geo_point GEOGRAPHY(POINT,4326), -- For spatial queries
    is_primary BOOLEAN DEFAULT FALSE,
    meta JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_addresses_geo ON user_addresses USING GIST(geo_point);
