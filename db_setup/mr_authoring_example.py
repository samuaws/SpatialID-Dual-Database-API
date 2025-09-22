import psycopg2
import json
from query_spatial_data import connect_to_postgis_db, connect_to_attributes_db, query_postgis_data, query_attributes_data, get_combined_data

class MRAuthoringSystem:
    def __init__(self):
        # Initialize database connections
        self.postgis_conn = connect_to_postgis_db()
        self.attributes_conn = connect_to_attributes_db()
        
        if not self.postgis_conn or not self.attributes_conn:
            raise Exception("Failed to connect to one or both databases")
    
    def close_connections(self):
        """Close database connections"""
        if self.postgis_conn:
            self.postgis_conn.close()
        if self.attributes_conn:
            self.attributes_conn.close()
    
    def get_spatial_data(self, spatial_id, zoom_level):
        """Get spatial geometry data from PostGIS"""
        try:
            # Use the query_postgis_data function which handles both remote and local databases
            result = query_postgis_data(spatial_id, zoom_level)
            
            if result:
                # Handle different result formats from the two databases
                if isinstance(result, dict):  # Remote database result
                    return result["geometry"]
                else:  # Local mock database result
                    return result
            return None
        except Exception as e:
            print(f"Error querying PostGIS data: {e}")
            return None
    
    def get_mr_attributes(self, spatial_id, zoom_level):
        """Get MR-specific attributes from the attributes database"""
        try:
            # Use the query_attributes_data function
            return query_attributes_data(spatial_id, zoom_level)
        except Exception as e:
            print(f"Error querying attributes data: {e}")
            return None
    
    def save_mr_attributes(self, spatial_id, zoom_level, attributes):
        """Save or update MR attributes in the attributes database"""
        try:
            cursor = self.attributes_conn.cursor()
            query = """INSERT INTO spatial_attributes (spatial_id, zoom_level, attributes)
                      VALUES (%s, %s, %s)
                      ON CONFLICT (spatial_id, zoom_level) 
                      DO UPDATE SET attributes = %s, updated_at = CURRENT_TIMESTAMP"""
            cursor.execute(query, (spatial_id, zoom_level, json.dumps(attributes), json.dumps(attributes)))
            self.attributes_conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Error saving attributes: {e}")
            self.attributes_conn.rollback()
            return False
    
    def get_combined_mr_data(self, spatial_id, zoom_level):
        """Get combined spatial and MR attribute data"""
        # Use the get_combined_data function which handles both databases
        combined_data = get_combined_data(spatial_id, zoom_level)
        
        # Format the result to match the expected structure
        return {
            "spatial_id": spatial_id,
            "zoom_level": zoom_level,
            "geometry": combined_data.get("geometry"),
            "mr_attributes": combined_data.get("attributes") or {}
        }
    
    def get_viewport_data(self, viewport_spatial_ids, zoom_level):
        """Get data for multiple spatial IDs in a viewport"""
        results = []
        
        for spatial_id in viewport_spatial_ids:
            data = self.get_combined_mr_data(spatial_id, zoom_level)
            if data["geometry"] is not None:  # Only include if geometry exists
                results.append(data)
        
        return results

# Example usage for MR Authoring
def main():
    # Initialize the MR Authoring system
    try:
        mr_system = MRAuthoringSystem()
    except Exception as e:
        print(f"Failed to initialize MR system: {e}")
        return
    
    try:
        # Example: Create MR annotation for a building
        building_spatial_id = "example_building_id"
        zoom_level = 15
        
        # MR-specific attributes for a building
        building_mr_attributes = {
            "type": "building",
            "mr_annotations": [
                {
                    "id": "anno1",
                    "type": "text",
                    "content": "Main Entrance",
                    "position": {"x": 120.5, "y": 0, "z": 50.2},
                    "rotation": {"x": 0, "y": 90, "z": 0},
                    "scale": 1.0,
                    "color": "#FFFFFF"
                },
                {
                    "id": "anno2",
                    "type": "highlight",
                    "color": "#FF0000",
                    "opacity": 0.5,
                    "target": "window_3f_east"
                }
            ],
            "interaction": {
                "clickable": True,
                "highlight_on_hover": True,
                "custom_action": "show_building_info"
            },
            "metadata": {
                "name": "Office Building A",
                "height": 45.5,
                "floors": 12,
                "construction_year": 2010,
                "last_renovation": 2022
            }
        }
        
        # Save the MR attributes
        success = mr_system.save_mr_attributes(building_spatial_id, zoom_level, building_mr_attributes)
        if success:
            print(f"Successfully saved MR attributes for building {building_spatial_id}")
        else:
            print(f"Failed to save MR attributes for building {building_spatial_id}")
        
        # Retrieve the combined data
        building_data = mr_system.get_combined_mr_data(building_spatial_id, zoom_level)
        print("\nCombined building data:")
        print(json.dumps(building_data, indent=2))
        
        # Example: Get data for multiple spatial IDs in a viewport
        viewport_spatial_ids = ["example_building_id", "nearby_road_id", "park_area_id"]
        viewport_data = mr_system.get_viewport_data(viewport_spatial_ids, zoom_level)
        print(f"\nFound {len(viewport_data)} objects in viewport")
        
    finally:
        # Close database connections
        mr_system.close_connections()

if __name__ == "__main__":
    main()