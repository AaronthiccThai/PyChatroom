CREATE DATABASE chatdb;

\c chatdb

CREATE USER admin WITH PASSWORD 'admin';
GRANT ALL PRIVILEGES ON DATABASE chatdb TO admin;

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL CHECK (char_length(password) > 5)
);

GRANT ALL PRIVILEGES ON TABLE users TO admin;

GRANT USAGE, SELECT ON SEQUENCE users_id_seq TO admin;
