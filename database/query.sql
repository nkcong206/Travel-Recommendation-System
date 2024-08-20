-- Enable PostGIS and vector extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS vector;

-- Drop the existing schema if it exists
DROP SCHEMA IF EXISTS travel_database CASCADE;
CREATE SCHEMA IF NOT EXISTS travel_database;
SET search_path TO travel_database;

-- Create a custom type for the Address structure
CREATE TYPE Address AS (
    street TEXT,
    district TEXT,
    city TEXT
);

-- Create the Hotel table with an embedding vector column
CREATE TABLE Hotel (
    hotel_id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    address Address,
    location GEOGRAPHY(POINT, 4326),  -- PostGIS geography type for location data
    rating DECIMAL(2, 1),
    description TEXT,
    embedding vector(768),  -- Using the vector extension for 768-dimensional embeddings
    img_url JSON,
    comments JSON
);

-- Create an index on the district of the Address and Rating columns for the Hotel table
CREATE INDEX idx_hotel_address_rating ON Hotel(((address).district), rating);

-- Create the Price table for the Hotel table
CREATE TABLE HotelPrice (
    hprice_id SERIAL PRIMARY KEY,
    hotel_id INT REFERENCES Hotel(hotel_id) ON DELETE CASCADE,
    room_type VARCHAR(255),
    capacity INT,
    price INT NOT NULL
);

-- Create an index on the hotel_id for the HotelPrice table
CREATE INDEX idx_hotelprice_hotel_id ON HotelPrice(hotel_id);

-- Create the TouristAttraction table with an embedding vector column
CREATE TABLE TouristAttraction (
    attraction_id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    address Address,
    location GEOGRAPHY(POINT, 4326),  -- PostGIS geography type for location data
    attraction_type VARCHAR(255),
    rating DECIMAL(2, 1),
    description TEXT,
    embedding vector(768),  -- Using the vector extension for 768-dimensional embeddings
    img_url JSON,
    comments JSON
);

-- Create an index on the district of the Address and Rating columns for the TouristAttraction table
CREATE INDEX idx_attraction_address_rating ON TouristAttraction(((address).district), rating);

-- Create the Price table for the TouristAttraction table
CREATE TABLE AttractionPrice (
    aprice_id SERIAL PRIMARY KEY,
    attraction_id INT REFERENCES TouristAttraction(attraction_id) ON DELETE CASCADE,
    ticket_type VARCHAR(255),
    number_people INT,
    price INT NOT NULL
);

-- Create an index on the attraction_id for the AttractionPrice table
CREATE INDEX idx_attractionprice_attraction_id ON AttractionPrice(attraction_id);

-- Create the Restaurant table with an embedding vector column
CREATE TABLE Restaurant (
    res_id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    address Address,
    location GEOGRAPHY(POINT, 4326),  -- PostGIS geography type for location data
    rating DECIMAL(2, 1),
    embedding vector(768),  -- Using the vector extension for 768-dimensional embeddings
    description TEXT,
    img_url JSON,
    comments JSON
);

-- Create an index on the district of the Address and Rating columns for the Restaurant table
CREATE INDEX idx_res_address_rating ON Restaurant(((address).district), rating);
