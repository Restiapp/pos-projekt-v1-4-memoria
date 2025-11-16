# Adatbázis Séma (PostgreSQL)

A séma a normalizálást követi, de a `JSONB` típust használja a rugalmasság érdekében, különösen a termékmódosítók és egyedi attribútumok esetében.

```sql
-- Module 0: Terméktörzs és Menü
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    parent_id INTEGER REFERENCES categories(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    base_price NUMERIC(10, 2) NOT NULL,
    category_id INTEGER REFERENCES categories(id),
    sku VARCHAR(100) UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    translations JSONB, -- {'en': {'name': '..', 'desc': '..'}, 'de': {'name': '..', 'desc': '..'}}
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE image_assets (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id),
    gcs_url_original TEXT NOT NULL,
    gcs_urls_resized JSONB, -- {'thumbnail': 'url', 'medium': 'url'}
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE modifier_groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    selection_type VARCHAR(50) NOT NULL, -- 'SINGLE_CHOICE_REQUIRED', 'MULTIPLE_CHOICE_OPTIONAL'
    min_selection INT DEFAULT 0,
    max_selection INT DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE modifiers (
    id SERIAL PRIMARY KEY,
    group_id INTEGER NOT NULL REFERENCES modifier_groups(id),
    name VARCHAR(255) NOT NULL,
    price_modifier NUMERIC(10, 2) DEFAULT 0.00,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE product_modifier_group_associations (
    product_id INTEGER NOT NULL REFERENCES products(id),
    group_id INTEGER NOT NULL REFERENCES modifier_groups(id),
    PRIMARY KEY (product_id, group_id)
);

CREATE TABLE channel_visibility (
    id SERIAL PRIMARY KEY,
    channel_name VARCHAR(100) NOT NULL, -- 'Pult', 'Kiszállítás', 'Helybeni'
    product_id INTEGER REFERENCES products(id),
    price_override NUMERIC(10, 2),
    is_visible BOOLEAN DEFAULT TRUE,
    UNIQUE(channel_name, product_id)
);

-- Module 1, 2, 3, 4: Rendelések, Asztalok, KDS, Fizetés
CREATE TABLE tables (
    id SERIAL PRIMARY KEY,
    table_number VARCHAR(50) UNIQUE NOT NULL,
    position_x INT,
    position_y INT,
    capacity INT
);

CREATE TABLE seats (
    id SERIAL PRIMARY KEY,
    table_id INTEGER REFERENCES tables(id),
    seat_number INT NOT NULL,
    UNIQUE(table_id, seat_number)
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    order_type VARCHAR(50) NOT NULL, -- 'Helyben', 'Elvitel', 'Kiszállítás'
    status VARCHAR(50) NOT NULL DEFAULT 'NYITOTT', -- 'NYITOTT', 'FELDOLGOZVA', 'LEZART', 'SZTORNÓ'
    table_id INTEGER REFERENCES tables(id),
    total_amount NUMERIC(10, 2),
    final_vat_rate NUMERIC(4, 2) DEFAULT 27.00,
    ntak_data JSONB, -- 'Rendelésösszesítő' adatai
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id),
    product_id INTEGER NOT NULL REFERENCES products(id),
    seat_id INTEGER REFERENCES seats(id),
    quantity INT NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL,
    selected_modifiers JSONB, -- [{'group_name': 'Zsemle', 'modifier_name': 'Szezamos', 'price': 0.00}]
    kds_station VARCHAR(50), -- 'Konyha', 'Pizza', 'Pult'
    kds_status VARCHAR(50) DEFAULT 'VÁRAKOZIK'
);

CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id),
    payment_method VARCHAR(100) NOT NULL, -- 'Készpénz', 'Bankkártya', 'OTP SZÉP', 'K&H SZÉP', 'MKB SZÉP'
    amount NUMERIC(10, 2) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Module 5: Készletkezelés
CREATE TABLE inventory_items (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    unit VARCHAR(50) NOT NULL, -- 'kg', 'liter', 'db'
    current_stock_perpetual NUMERIC(10, 3) DEFAULT 0.000, -- Automatikus raktár
    last_cost_per_unit NUMERIC(10, 2)
);

CREATE TABLE recipes (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id),
    inventory_item_id INTEGER NOT NULL REFERENCES inventory_items(id),
    quantity_used NUMERIC(10, 3) NOT NULL
);

CREATE TABLE supplier_invoices (
    id SERIAL PRIMARY KEY,
    supplier_name VARCHAR(255),
    invoice_date DATE,
    total_amount NUMERIC(10, 2),
    ocr_data JSONB,
    status VARCHAR(50) DEFAULT 'FELDOLGOZÁSRA VÁR'
);

CREATE TABLE daily_inventory_sheets ( -- A 'napi karton' definíciója
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE daily_inventory_sheet_items (
    sheet_id INTEGER REFERENCES daily_inventory_sheets(id),
    inventory_item_id INTEGER REFERENCES inventory_items(id),
    PRIMARY KEY(sheet_id, inventory_item_id)
);

CREATE TABLE daily_inventory_counts ( -- A tényleges napi leltár
    id SERIAL PRIMARY KEY,
    sheet_id INTEGER REFERENCES daily_inventory_sheets(id),
    count_date DATE NOT NULL,
    employee_id INTEGER, -- REFERENCES employees(id)
    counts JSONB, -- {'item_id_1': 10.5, 'item_id_2': 100}
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Module 6 & 7: Munkatárs és CRM
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    pin_code_hash TEXT,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    role_name VARCHAR(100) UNIQUE NOT NULL -- 'Admin', 'Pultos', 'Szakács'
);

CREATE TABLE permissions (
    id SERIAL PRIMARY KEY,
    permission_key VARCHAR(255) UNIQUE NOT NULL -- 'CAN_OPEN_CASH_DRAWER', 'CAN_EDIT_PRODUCTS'
);

CREATE TABLE role_permissions (
    role_id INTEGER REFERENCES roles(id),
    permission_id INTEGER REFERENCES permissions(id),
    PRIMARY KEY(role_id, permission_id)
);

CREATE TABLE employee_roles (
    employee_id INTEGER REFERENCES employees(id),
    role_id INTEGER REFERENCES roles(id),
    PRIMARY KEY(employee_id, role_id)
);

CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(50),
    loyalty_points INT DEFAULT 0,
    credit_balance NUMERIC(10, 2) DEFAULT 0.00
);
```
