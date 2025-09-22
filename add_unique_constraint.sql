-- Add a unique constraint to the spatial_attributes table
ALTER TABLE spatial_attributes ADD CONSTRAINT spatial_attributes_unique_spatial_id_zoom UNIQUE (spatial_id, zoom_level);