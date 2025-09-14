-- Add latitude and longitude columns to restaurants table
ALTER TABLE restaurants 
ADD COLUMN IF NOT EXISTS latitude DECIMAL(10, 8),
ADD COLUMN IF NOT EXISTS longitude DECIMAL(11, 8);

-- Create index for faster coordinate-based queries
CREATE INDEX IF NOT EXISTS idx_restaurants_coordinates ON restaurants(latitude, longitude);

-- Update existing restaurants with coordinates from the location geography field
UPDATE restaurants 
SET 
    latitude = ST_Y(location::geometry),
    longitude = ST_X(location::geometry)
WHERE location IS NOT NULL 
AND latitude IS NULL 
AND longitude IS NULL;
