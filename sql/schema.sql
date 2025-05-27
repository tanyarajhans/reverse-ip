-- This SQL script creates the necessary table for storing reverse IP addresses with an auto-incrementing ID and a timestamp.

CREATE TABLE reverse_ips (
    id SERIAL PRIMARY KEY,
    ip TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
