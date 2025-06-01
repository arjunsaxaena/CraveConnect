-----------------------------
-- Order Management System
-----------------------------
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    delivery_address_id UUID NOT NULL REFERENCES user_addresses(id),
    subtotal NUMERIC(10,2) NOT NULL,
    tax_amount NUMERIC(10,2) NOT NULL,
    delivery_fee NUMERIC(10,2) NOT NULL,
    tip_amount NUMERIC(10,2) DEFAULT 0.00,
    total_amount NUMERIC(10,2) NOT NULL,
    special_instructions TEXT,
    status TEXT CHECK (
        status IN (
            'pending', 'confirmed', 'preparing', 
            'ready_for_pickup', 'out_for_delivery', 
            'delivered', 'cancelled'
        )
    ) DEFAULT 'pending',
    scheduled_delivery_time TIMESTAMP,
    actual_delivery_time TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE order_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    menu_item_id UUID NOT NULL REFERENCES menu_items(id),
    quantity INT NOT NULL CHECK (quantity > 0),
    price_at_order NUMERIC(8,2) NOT NULL,
    customization JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);