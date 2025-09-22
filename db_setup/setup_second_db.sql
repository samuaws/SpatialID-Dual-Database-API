-- Create a new database for additional spatial data
CREATE DATABASE spatial_attributes_db;

-- Connect to the new database
\c spatial_attributes_db;

-- Create a table to store additional attributes linked by Spatial ID
CREATE TABLE spatial_attributes (
    id SERIAL PRIMARY KEY,
    spatial_id VARCHAR(255) NOT NULL,
    zoom_level INTEGER NOT NULL,
    attributes JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for efficient querying
CREATE INDEX idx_spatial_id ON spatial_attributes(spatial_id);
CREATE INDEX idx_zoom_level ON spatial_attributes(zoom_level);
CREATE INDEX idx_spatial_id_zoom ON spatial_attributes(spatial_id, zoom_level);

-- Add extension for dblink (to connect to external PostgreSQL databases)
CREATE EXTENSION dblink;

-- Create a function to query data from both databases
CREATE OR REPLACE FUNCTION get_combined_spatial_data(p_spatial_id VARCHAR, p_zoom_level INTEGER)
RETURNS TABLE (
    spatial_id VARCHAR,
    geometry JSONB,  -- Assuming geometry is stored as JSONB in the result
    attributes JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p_spatial_id,
        geometry_data.geometry,
        sa.attributes
    FROM 
        dblink('host=1337.tlab.cloud port=1337 dbname=spatial_id_db user=postgres password=tlab',
               format('SELECT geometry FROM spatial_data WHERE spatial_id = ''%s'' AND zoom_level = %s', 
                      p_spatial_id, p_zoom_level))
        AS geometry_data(geometry JSONB)
    LEFT JOIN spatial_attributes sa ON sa.spatial_id = p_spatial_id AND sa.zoom_level = p_zoom_level;
END;
$$ LANGUAGE plpgsql;

-- Create a sample insert function
CREATE OR REPLACE FUNCTION add_spatial_attribute(p_spatial_id VARCHAR, p_zoom_level INTEGER, p_attributes JSONB)
RETURNS VOID AS $$
BEGIN
    INSERT INTO spatial_attributes (spatial_id, zoom_level, attributes)
    VALUES (p_spatial_id, p_zoom_level, p_attributes)
    ON CONFLICT (spatial_id, zoom_level) 
    DO UPDATE SET attributes = p_attributes, updated_at = CURRENT_TIMESTAMP;
END;
$$ LANGUAGE plpgsql;