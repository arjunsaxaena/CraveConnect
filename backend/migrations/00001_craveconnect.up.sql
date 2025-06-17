create extension if not exists vector;
create extension if not exists pgcrypto;



create type auth_provider as enum ('google', 'apple', 'phone');

create type vehicle_type as enum ('bike', 'car', 'scooter', 'bicycle');

create type file_type as enum ('menu', 'profile_image', 'vehicle_image', 'restaurant_logo', 'other');

create type payment_status as enum ('initiated', 'success', 'failed', 'refunded');

create type spice_tolerance as enum ('low', 'medium', 'high');



create table users (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  email text unique not null,
  provider auth_provider not null,
  address jsonb,
  created_at timestamptz default now(),
  updated_at timestamptz default now(),
  meta jsonb
);

create table restaurants (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  address jsonb,
  owner_id uuid references users (id),
  created_at timestamptz default now(),
  updated_at timestamptz default now(),
  meta jsonb
);

create table menu_items (
  id uuid primary key default gen_random_uuid(),
  restaurant_id uuid references restaurants (id),
  name text not null,
  description text,
  tags text[],
  allergens text[],
  created_at timestamptz default now(),
  updated_at timestamptz default now(),
  meta jsonb
);

create table menu_item_options (
  id uuid primary key default gen_random_uuid(),
  menu_item_id uuid references menu_items (id),
  name text not null,         -- e.g., 'Small', 'Medium', 'Large'
  description text,
  price numeric(10,2) not null,
  meta jsonb,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create table addons (
  id uuid primary key default gen_random_uuid(),
  name text not null,         -- e.g., 'Extra Cheese'
  description text,
  price numeric(10,2) not null,
  meta jsonb,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create table menu_item_addons (
  menu_item_id uuid references menu_items (id),
  addon_id uuid references addons (id),
  primary key (menu_item_id, addon_id)
);

create table favorites (
  user_id uuid references users (id),
  menu_item_id uuid references menu_items (id),
  created_at timestamptz default now(),
  updated_at timestamptz default now(),
  meta jsonb,
  primary key (user_id, menu_item_id)
);

create table promotions (
  id uuid primary key default gen_random_uuid(),
  restaurant_id uuid references restaurants (id),
  title text not null,
  description text,
  discount_percent numeric(5,2),
  valid_from timestamptz,
  valid_to timestamptz,
  created_at timestamptz default now(),
  updated_at timestamptz default now(),
  meta jsonb
);

create table orders (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users (id),
  restaurant_id uuid references restaurants (id),
  total_price numeric(10, 2) not null,
  created_at timestamptz default now(),
  updated_at timestamptz default now(),
  meta jsonb
);

create table queries (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users (id),
  query_text text not null,
  context jsonb,
  feedback text,
  created_at timestamptz default now(),
  updated_at timestamptz default now(),
  meta jsonb
);

create table delivery_persons (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users (id),
  name text not null,
  phone_number text unique not null,
  vehicle_details text,
  vehicle_type vehicle_type not null,
  created_at timestamptz default now(),
  updated_at timestamptz default now(),
  meta jsonb
);

create table order_assignments (
  id uuid primary key default gen_random_uuid(),
  order_id uuid references orders (id),
  delivery_person_id uuid references delivery_persons (id),
  assigned_at timestamptz default now(),
  updated_at timestamptz default now(),
  meta jsonb
);

create table reviews (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users (id),
  restaurant_id uuid references restaurants (id),
  rating int check (rating >= 1 and rating <= 5),
  comment text,
  created_at timestamptz default now(),
  updated_at timestamptz default now(),
  meta jsonb
);



create table files (
  id uuid primary key default gen_random_uuid(),
  file_url text not null,
  file_type file_type,
  uploaded_by uuid references users (id),
  created_at timestamptz default now(),
  updated_at timestamptz default now(),
  meta jsonb
);



create table recommendations (
  id uuid primary key default gen_random_uuid(),
  query_id uuid references queries (id),
  menu_item_id uuid references menu_items (id),
  confidence_score numeric(5, 4),
  created_at timestamptz default now(),
  updated_at timestamptz default now(),
  meta jsonb
);

create table menu_item_embeddings (
  menu_item_id uuid references menu_items (id) primary key,
  embedding vector(768),
  created_at timestamptz default now(),
  updated_at timestamptz default now(),
  meta jsonb
);

create table user_preferences (
  user_id uuid references users (id) primary key,
  preferred_cuisines text[],
  dietary_restrictions text[],
  spice_tolerance spice_tolerance,
  allergies text[],
  created_at timestamptz default now(),
  updated_at timestamptz default now(),
  meta jsonb
);



create table payments (
  id uuid primary key default gen_random_uuid(),
  order_id uuid references orders (id),
  amount numeric(10,2) not null,
  status payment_status not null,
  provider text,
  created_at timestamptz default now(),
  updated_at timestamptz default now(),
  meta jsonb
);

create table notifications (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users (id),
  title text not null,
  body text,
  seen boolean default false,
  created_at timestamptz default now(),
  updated_at timestamptz default now(),
  meta jsonb
);
