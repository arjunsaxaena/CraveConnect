CREATE TYPE file_purpose AS ENUM (
    'restaurant_image',
    'menu_image',
    'menu_item_image',
    'review_photo'
);

CREATE TABLE files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    uploader_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    storage_path TEXT NOT NULL UNIQUE,
    original_filename TEXT NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    file_size BIGINT NOT NULL CHECK (file_size > 0),
    dimensions JSONB,  -- Stores {width, height} for images
    checksum TEXT NOT NULL UNIQUE,  -- For duplicate detection
    purpose file_purpose NOT NULL,
    is_public BOOLEAN DEFAULT TRUE,
    meta JSONB DEFAULT '{}',
    deleted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_files_purpose ON files(purpose);
CREATE INDEX idx_files_uploader ON files(uploader_id);
