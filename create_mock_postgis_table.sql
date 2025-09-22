-- Create a mock spatial_data table to simulate the PostGIS database
CREATE TABLE IF NOT EXISTS spatial_data (
    id SERIAL PRIMARY KEY,
    spatial_id VARCHAR(255) NOT NULL,
    zoom_level INTEGER NOT NULL,
    geometry GEOMETRY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT spatial_data_unique_spatial_id_zoom UNIQUE (spatial_id, zoom_level)
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_spatial_data_spatial_id ON spatial_data(spatial_id);
CREATE INDEX IF NOT EXISTS idx_spatial_data_zoom_level ON spatial_data(zoom_level);
CREATE INDEX IF NOT EXISTS idx_spatial_data_geometry ON spatial_data USING GIST(geometry);

-- Insert some sample data
INSERT INTO spatial_data (spatial_id, zoom_level, geometry)
VALUES 
('test123', 5, ST_GeomFromText('POINT(0 0)')),
('test123', 10, ST_GeomFromText('POINT(0 0)')),
('building1', 5, ST_GeomFromText('POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))')),
('road1', 5, ST_GeomFromText('LINESTRING(0 0, 1 1, 2 2)'));