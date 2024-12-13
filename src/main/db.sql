CREATE DATABASE chatdb;

\c chatdb

CREATE USER admin WITH PASSWORD 'admin';
GRANT ALL PRIVILEGES ON DATABASE chatdb TO admin;

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL CHECK (char_length(password) > 5)
);

CREATE TABLE active_users (
    websocket_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    CONSTRAINT fk_username FOREIGN KEY (username) REFERENCES users (username)
);

GRANT ALL PRIVILEGES ON TABLE active_users TO admin;

GRANT USAGE, SELECT ON SEQUENCE users_id_seq TO admin;
GRANT USAGE, SELECT ON SEQUENCE active_users_websocket_id_seq TO admin;