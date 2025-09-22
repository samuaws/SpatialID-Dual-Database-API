import sys
import os
import json
import psycopg2

# Add the db_setup directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'db_setup'))

# Import the connection function for the attributes database
from query_spatial_data import connect_to_attributes_db

# Create a simplified version of the MR authoring system that only uses the attributes database
class SimpleMRAuthoringSystem:
    def __init__(self):
        # Initialize database connection to the attributes database only
        self.attributes_conn = connect_to_attributes_db()
        
        if not self.attributes_conn:
            raise Exception("Failed to connect to the attributes database")
    
    def close_connections(self):
        """Close database connections"""
        if self.attributes_conn:
            self.attributes_conn.close()
    
    def get_mr_attributes(self, spatial_id, zoom_level):
        """Get MR-specific attributes from the attributes database"""
        try:
            cursor = self.attributes_conn.cursor()
            query = """SELECT attributes FROM spatial_attributes 
                      WHERE spatial_id = %s AND zoom_level = %s"""
            cursor.execute(query, (spatial_id, zoom_level))
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                return result[0]  # Assuming attributes is the first column
            return None
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

def test_mr_authoring_system():
    try:
        # Create an instance of the simplified MR authoring system
        print("Initializing Simple MR Authoring System (local database only)...")
        mr_system = SimpleMRAuthoringSystem()
        print("Simple MR Authoring System initialized successfully!\n")
        
        # Test getting MR attributes for our test record
        spatial_id = "test123"
        zoom_level = 5
        
        print(f"Retrieving MR attributes for Spatial ID: {spatial_id}, Zoom Level: {zoom_level}")
        attributes = mr_system.get_mr_attributes(spatial_id, zoom_level)
        
        if attributes:
            print("Successfully retrieved attributes:")
            print(json.dumps(attributes, indent=2))
            
            # Test saving updated attributes
            print("\nUpdating attributes with a new annotation...")
            
            # Add a new annotation
            if 'annotations' in attributes:
                attributes['annotations'].append({
                    "type": "arrow",
                    "direction": {"x": 1, "y": 0, "z": 0},
                    "length": 2.5,
                    "color": "#00FF00"
                })
            else:
                attributes['annotations'] = [{
                    "type": "arrow",
                    "direction": {"x": 1, "y": 0, "z": 0},
                    "length": 2.5,
                    "color": "#00FF00"
                }]
            
            # Save the updated attributes
            success = mr_system.save_mr_attributes(spatial_id, zoom_level, attributes)
            
            if success:
                print("Successfully saved updated attributes!")
                
                # Retrieve the updated attributes to verify
                updated_attributes = mr_system.get_mr_attributes(spatial_id, zoom_level)
                print("\nRetrieved updated attributes:")
                print(json.dumps(updated_attributes, indent=2))
            else:
                print("Failed to save updated attributes.")
        else:
            print(f"No attributes found for Spatial ID: {spatial_id}, Zoom Level: {zoom_level}")
        
        # Close database connections
        mr_system.close_connections()
        print("\nDatabase connections closed.")
        
    except Exception as e:
        print(f"Error testing MR authoring system: {e}")

if __name__ == "__main__":
    test_mr_authoring_system()