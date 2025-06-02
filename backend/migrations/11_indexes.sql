_-----------------------------
-- Indexes & Performance
-----------------------------
CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_orders_restaurant ON orders(restaurant_id);
CREATE INDEX idx_menu_items_restaurant ON menu_items(restaurant_id);
CREATE INDEX idx_deliveries_partner ON deliveries(partner_id);
CREATE INDEX idx_user_interactions ON user_food_interactions(user_id, menu_item_id);