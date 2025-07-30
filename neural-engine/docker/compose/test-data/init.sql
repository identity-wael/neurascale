-- Test database initialization script
-- Creates necessary schemas and test data for integration tests

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create test schema
CREATE SCHEMA IF NOT EXISTS test;

-- Create test tables
CREATE TABLE IF NOT EXISTS test.devices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'disconnected',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS test.sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    device_id UUID REFERENCES test.devices(id),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    status VARCHAR(50) DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS test.neural_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES test.sessions(id),
    timestamp TIMESTAMP NOT NULL,
    channel INTEGER NOT NULL,
    value FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_neural_data_session_timestamp ON test.neural_data(session_id, timestamp);
CREATE INDEX idx_neural_data_channel ON test.neural_data(channel);

-- Insert test data
INSERT INTO test.devices (name, type, status) VALUES
    ('Test Device 1', 'EEG', 'connected'),
    ('Test Device 2', 'EMG', 'disconnected'),
    ('Test Device 3', 'ECG', 'connected');

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA test TO neural;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA test TO neural;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA test TO neural;
