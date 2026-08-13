-- Database initialization script for Facial Recognition Attendance System
-- This script runs automatically when the PostgreSQL container starts for the first time.

-- Enable pgvector extension for face embedding storage and similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- Enable pg_trgm for text search optimization
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'Database initialized with pgvector and pg_trgm extensions.';
END $$;
