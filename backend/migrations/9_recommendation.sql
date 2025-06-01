-----------------------------
-- AI Recommendation System
-----------------------------
CREATE TABLE user_food_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    menu_item_id UUID NOT NULL REFERENCES menu_items(id),
    interaction_type TEXT CHECK (
        interaction_type IN ('view', 'order', 'rating', 'search')
    ),
    rating_value NUMERIC(2,1) CHECK (
        rating_value BETWEEN 0.0 AND 5.0
    ),
    search_query TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE recommendation_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_name TEXT NOT NULL,
    model_version TEXT NOT NULL,
    model_data BYTEA NOT NULL,
    training_date TIMESTAMP NOT NULL,
    accuracy NUMERIC(5,4),
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);