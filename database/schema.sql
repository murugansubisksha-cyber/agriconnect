-- =========================================================
-- AgriConnect - AI Powered Direct Farmer Marketplace
-- Database Schema (SQLite)
-- =========================================================
-- Generated to exactly match backend/models.py (SQLAlchemy).
-- Tables are ordered so that every FOREIGN KEY target already
-- exists by the time it is referenced.
-- =========================================================

PRAGMA foreign_keys = ON;

-- =========================================================
-- 1. FARMERS
-- =========================================================
CREATE TABLE IF NOT EXISTS farmers (
    farmer_id           INTEGER PRIMARY KEY AUTOINCREMENT,

    full_name           VARCHAR(120) NOT NULL,
    mobile_number       VARCHAR(15)  NOT NULL UNIQUE,
    email                VARCHAR(120) UNIQUE,
    password_hash        VARCHAR(255) NOT NULL,
    aadhaar_number       VARCHAR(20)  UNIQUE,

    verified_farmer       BOOLEAN NOT NULL DEFAULT 0,
    farmer_badge          VARCHAR(50),

    farm_name             VARCHAR(150),
    farm_location          VARCHAR(255),
    district               VARCHAR(100),
    state                  VARCHAR(100),
    pincode                VARCHAR(10),
    latitude               FLOAT,
    longitude              FLOAT,
    farming_method         VARCHAR(20),

    profile_photo           VARCHAR(255),
    farm_photo               VARCHAR(255),

    total_products            INTEGER NOT NULL DEFAULT 0,
    total_orders                INTEGER NOT NULL DEFAULT 0,
    average_rating                FLOAT NOT NULL DEFAULT 0.0,
    total_reviews                   INTEGER NOT NULL DEFAULT 0,

    registration_date                 DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    active_status                       BOOLEAN NOT NULL DEFAULT 1,
    created_at                           DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at                             DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT ck_farmer_farming_method CHECK (farming_method IN ('Organic', 'Conventional', 'Natural')),
    CONSTRAINT ck_farmer_avg_rating CHECK (average_rating >= 0 AND average_rating <= 5)
);

CREATE INDEX IF NOT EXISTS ix_farmers_mobile_number ON farmers (mobile_number);
CREATE INDEX IF NOT EXISTS ix_farmers_email ON farmers (email);
CREATE INDEX IF NOT EXISTS ix_farmers_district ON farmers (district);

-- =========================================================
-- 2. CUSTOMERS
-- =========================================================
CREATE TABLE IF NOT EXISTS customers (
    customer_id         INTEGER PRIMARY KEY AUTOINCREMENT,

    full_name            VARCHAR(120) NOT NULL,
    mobile_number         VARCHAR(15)  NOT NULL UNIQUE,
    email                  VARCHAR(120) UNIQUE,
    password_hash            VARCHAR(255) NOT NULL,
    profile_photo              VARCHAR(255),

    address                     VARCHAR(255),
    district                      VARCHAR(100),
    state                          VARCHAR(100),
    pincode                         VARCHAR(10),
    latitude                         FLOAT,
    longitude                          FLOAT,

    reliability_score                    FLOAT NOT NULL DEFAULT 50.0,
    successful_orders                      INTEGER NOT NULL DEFAULT 0,
    cancelled_orders                         INTEGER NOT NULL DEFAULT 0,
    total_orders                               INTEGER NOT NULL DEFAULT 0,
    average_rating                               FLOAT NOT NULL DEFAULT 0.0,

    created_at                                     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at                                       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    active_status                                      BOOLEAN NOT NULL DEFAULT 1,

    CONSTRAINT ck_customer_reliability CHECK (reliability_score >= 0 AND reliability_score <= 100),
    CONSTRAINT ck_customer_avg_rating CHECK (average_rating >= 0 AND average_rating <= 5)
);

CREATE INDEX IF NOT EXISTS ix_customers_mobile_number ON customers (mobile_number);
CREATE INDEX IF NOT EXISTS ix_customers_email ON customers (email);
CREATE INDEX IF NOT EXISTS ix_customers_district ON customers (district);

-- =========================================================
-- 3. PRODUCTS  (belongs to a Farmer)
-- =========================================================
CREATE TABLE IF NOT EXISTS products (
    product_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    farmer_id               INTEGER NOT NULL,

    product_name              VARCHAR(150) NOT NULL,
    product_category            VARCHAR(80),
    description                   TEXT,

    harvest_date                    DATE,
    expiry_date                       DATE,

    available_quantity                  FLOAT NOT NULL DEFAULT 0.0,
    unit                                   VARCHAR(20) NOT NULL DEFAULT 'kg',

    base_price                              FLOAT NOT NULL,
    minimum_price                             FLOAT,

    product_image                               VARCHAR(255),

    delivery_available                            BOOLEAN NOT NULL DEFAULT 0,
    pickup_available                                BOOLEAN NOT NULL DEFAULT 1,

    stock_status                                      VARCHAR(20) NOT NULL DEFAULT 'In Stock',
    organic_certified                                   BOOLEAN NOT NULL DEFAULT 0,

    active_status                                         BOOLEAN NOT NULL DEFAULT 1,
    created_at                                              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at                                                DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT ck_product_base_price_positive CHECK (base_price > 0),
    CONSTRAINT ck_product_quantity_non_negative CHECK (available_quantity >= 0),
    CONSTRAINT ck_product_stock_status CHECK (stock_status IN ('In Stock', 'Low Stock', 'Out of Stock')),
    FOREIGN KEY (farmer_id) REFERENCES farmers (farmer_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_products_farmer_id ON products (farmer_id);
CREATE INDEX IF NOT EXISTS ix_products_category ON products (product_category);

-- =========================================================
-- 4. QUOTATIONS  (Customer offers on a Product)
-- =========================================================
CREATE TABLE IF NOT EXISTS quotations (
    quotation_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id              INTEGER NOT NULL,
    product_id                 INTEGER NOT NULL,

    offered_price                 FLOAT NOT NULL,
    requested_quantity               FLOAT NOT NULL,

    quotation_status                   VARCHAR(20) NOT NULL DEFAULT 'Pending',
    quotation_deadline                    DATETIME,
    distance_from_farmer                    FLOAT,

    ai_score                                  FLOAT,
    ai_recommended                              BOOLEAN NOT NULL DEFAULT 0,

    farmer_decision                               VARCHAR(20),
    explanation_text                                TEXT,

    created_at                                        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT ck_quotation_price_positive CHECK (offered_price > 0),
    CONSTRAINT ck_quotation_quantity_positive CHECK (requested_quantity > 0),
    CONSTRAINT ck_quotation_status CHECK (quotation_status IN ('Pending', 'Accepted', 'Rejected', 'Expired', 'Withdrawn')),
    FOREIGN KEY (customer_id) REFERENCES customers (customer_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products (product_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_quotations_customer_id ON quotations (customer_id);
CREATE INDEX IF NOT EXISTS ix_quotations_product_id ON quotations (product_id);

-- =========================================================
-- 5. AI_RECOMMENDATIONS  (advisory only, 1:1 with a Quotation)
-- =========================================================
CREATE TABLE IF NOT EXISTS ai_recommendations (
    recommendation_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    quotation_id              INTEGER NOT NULL UNIQUE,

    recommendation_score         FLOAT NOT NULL,
    price_score                     FLOAT,
    quantity_score                    FLOAT,
    distance_score                      FLOAT,
    reliability_score                     FLOAT,
    overall_score                           FLOAT,

    explanation                               TEXT,
    generated_time                              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT ck_ai_rec_score_range CHECK (recommendation_score >= 0 AND recommendation_score <= 100),
    FOREIGN KEY (quotation_id) REFERENCES quotations (quotation_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_ai_recommendations_quotation_id ON ai_recommendations (quotation_id);

-- =========================================================
-- 6. ORDERS  (created after a Farmer accepts a Quotation)
-- =========================================================
CREATE TABLE IF NOT EXISTS orders (
    order_id             INTEGER PRIMARY KEY AUTOINCREMENT,
    quotation_id            INTEGER UNIQUE,
    farmer_id                  INTEGER NOT NULL,
    customer_id                   INTEGER NOT NULL,

    total_amount                    FLOAT NOT NULL,
    delivery_charge                   FLOAT NOT NULL DEFAULT 0.0,

    payment_status                      VARCHAR(20) NOT NULL DEFAULT 'Pending',
    order_status                          VARCHAR(20) NOT NULL DEFAULT 'Requested',

    order_date                              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    packed_date                               DATETIME,
    shipped_date                                DATETIME,
    delivered_date                                DATETIME,

    created_at                                      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT ck_order_total_amount_positive CHECK (total_amount > 0),
    CONSTRAINT ck_order_status CHECK (order_status IN ('Requested', 'Accepted', 'Rejected', 'Packed', 'Out for Delivery', 'Delivered', 'Cancelled')),
    CONSTRAINT ck_order_payment_status CHECK (payment_status IN ('Pending', 'Paid', 'Failed', 'Refunded')),
    FOREIGN KEY (quotation_id) REFERENCES quotations (quotation_id) ON DELETE SET NULL,
    FOREIGN KEY (farmer_id) REFERENCES farmers (farmer_id) ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES customers (customer_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_orders_farmer_id ON orders (farmer_id);
CREATE INDEX IF NOT EXISTS ix_orders_customer_id ON orders (customer_id);
CREATE INDEX IF NOT EXISTS ix_orders_quotation_id ON orders (quotation_id);

-- =========================================================
-- 7. PAYMENTS  (1:1 with an Order)
-- =========================================================
CREATE TABLE IF NOT EXISTS payments (
    payment_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id                INTEGER NOT NULL UNIQUE,

    transaction_id             VARCHAR(100) UNIQUE,
    payment_method                VARCHAR(20) NOT NULL,
    payment_status                   VARCHAR(20) NOT NULL DEFAULT 'Pending',
    payment_amount                      FLOAT NOT NULL,
    payment_date                          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT ck_payment_amount_positive CHECK (payment_amount > 0),
    CONSTRAINT ck_payment_method CHECK (payment_method IN ('UPI', 'Debit Card', 'Credit Card', 'Net Banking', 'Cash on Delivery')),
    CONSTRAINT ck_payment_status CHECK (payment_status IN ('Pending', 'Success', 'Failed', 'Refunded')),
    FOREIGN KEY (order_id) REFERENCES orders (order_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_payments_order_id ON payments (order_id);

-- =========================================================
-- 8. REVIEWS  (Customer -> Farmer, one per completed Order)
-- =========================================================
CREATE TABLE IF NOT EXISTS reviews (
    review_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id             INTEGER NOT NULL,
    farmer_id                  INTEGER NOT NULL,
    order_id                     INTEGER NOT NULL UNIQUE,

    rating                          INTEGER NOT NULL,
    review_text                       TEXT,
    review_date                          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT ck_review_rating_range CHECK (rating >= 1 AND rating <= 5),
    FOREIGN KEY (customer_id) REFERENCES customers (customer_id) ON DELETE CASCADE,
    FOREIGN KEY (farmer_id) REFERENCES farmers (farmer_id) ON DELETE CASCADE,
    FOREIGN KEY (order_id) REFERENCES orders (order_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_reviews_customer_id ON reviews (customer_id);
CREATE INDEX IF NOT EXISTS ix_reviews_farmer_id ON reviews (farmer_id);

-- =========================================================
-- 9. CHATS  (polymorphic Farmer <-> Customer messaging)
-- =========================================================
CREATE TABLE IF NOT EXISTS chats (
    message_id           INTEGER PRIMARY KEY AUTOINCREMENT,

    sender_id                INTEGER NOT NULL,
    sender_type                 VARCHAR(10) NOT NULL,
    receiver_id                    INTEGER NOT NULL,
    receiver_type                     VARCHAR(10) NOT NULL,

    order_id                             INTEGER,

    message                                 TEXT,
    attachment                                 VARCHAR(255),

    sent_time                                    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    read_status                                     BOOLEAN NOT NULL DEFAULT 0,

    CONSTRAINT ck_chat_sender_type CHECK (sender_type IN ('farmer', 'customer')),
    CONSTRAINT ck_chat_receiver_type CHECK (receiver_type IN ('farmer', 'customer')),
    FOREIGN KEY (order_id) REFERENCES orders (order_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS ix_chats_sender_id ON chats (sender_id);
CREATE INDEX IF NOT EXISTS ix_chats_receiver_id ON chats (receiver_id);
CREATE INDEX IF NOT EXISTS ix_chats_order_id ON chats (order_id);

-- =========================================================
-- 10. NOTIFICATIONS  (polymorphic, Farmer or Customer)
-- =========================================================
CREATE TABLE IF NOT EXISTS notifications (
    notification_id      INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id                  INTEGER NOT NULL,
    user_type                   VARCHAR(10) NOT NULL,

    notification_title             VARCHAR(150) NOT NULL,
    notification_message              TEXT,
    notification_type                    VARCHAR(40) NOT NULL,

    is_read                                 BOOLEAN NOT NULL DEFAULT 0,
    created_at                                 DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT ck_notification_user_type CHECK (user_type IN ('farmer', 'customer')),
    CONSTRAINT ck_notification_type CHECK (
        notification_type IN (
            'Quotation Received', 'Order Accepted', 'Payment Success',
            'Delivery Update', 'AI Recommendation Ready'
        )
    )
);

CREATE INDEX IF NOT EXISTS ix_notifications_user_id ON notifications (user_id);

-- =========================================================
-- 11. BUYER_RELIABILITY  (1:1 detail breakdown for a Customer)
-- =========================================================
CREATE TABLE IF NOT EXISTS buyer_reliability (
    reliability_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id               INTEGER NOT NULL UNIQUE,

    successful_orders            INTEGER NOT NULL DEFAULT 0,
    cancelled_orders                INTEGER NOT NULL DEFAULT 0,
    return_percentage                  FLOAT NOT NULL DEFAULT 0.0,
    average_rating                        FLOAT NOT NULL DEFAULT 0.0,
    reliability_score                        FLOAT NOT NULL DEFAULT 50.0,

    CONSTRAINT ck_buyer_reliability_range CHECK (reliability_score >= 0 AND reliability_score <= 100),
    CONSTRAINT ck_buyer_return_pct_range CHECK (return_percentage >= 0 AND return_percentage <= 100),
    FOREIGN KEY (customer_id) REFERENCES customers (customer_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_buyer_reliability_customer_id ON buyer_reliability (customer_id);

-- =========================================================
-- 12. VOICE_ASSISTANT_LOGS  (audit log for voice commands)
-- =========================================================
CREATE TABLE IF NOT EXISTS voice_assistant_logs (
    log_id               INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id                  INTEGER NOT NULL,
    user_type                   VARCHAR(10),

    command                        TEXT NOT NULL,
    language                          VARCHAR(20) NOT NULL DEFAULT 'en',

    execution_status                     VARCHAR(20) NOT NULL DEFAULT 'Success',
    timestamp                               DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT ck_voice_log_execution_status CHECK (execution_status IN ('Success', 'Failed', 'Not Recognized'))
);

CREATE INDEX IF NOT EXISTS ix_voice_assistant_logs_user_id ON voice_assistant_logs (user_id);

-- =========================================================
-- End of Schema
-- =========================================================