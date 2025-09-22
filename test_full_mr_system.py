import sys
import os
import json

# Add the db_setup directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'db_setup'))

# Import the MRAuthoringSystem class
from mr_authoring_example import MRAuthoringSystem

def test_full_mr_system():
    try:
        # Create an instance of the MR authoring system
        print("Initializing Full MR Authoring System...")
        mr_system = MRAuthoringSystem()
        print("MR Authoring System initialized successfully!\n")
        
        # Test getting spatial data
        # Use a spatial_id that exists in the remote database
        spatial_id = "25/29/29801113/13210757"
        zoom_level = 5
        
        print(f"Retrieving spatial data for Spatial ID: {spatial_id}, Zoom Level: {zoom_level}")
        geometry = mr_system.get_spatial_data(spatial_id, zoom_level)
        
        if geometry:
            print("Successfully retrieved spatial geometry:")
            print(geometry)
        else:
            print(f"No spatial data found for Spatial ID: {spatial_id}, Zoom Level: {zoom_level}")
        
        # Test getting MR attributes
        print(f"\nRetrieving MR attributes for Spatial ID: {spatial_id}, Zoom Level: {zoom_level}")
        attributes = mr_system.get_mr_attributes(spatial_id, zoom_level)
        
        if attributes:
            print("Successfully retrieved attributes:")
            print(json.dumps(attributes, indent=2))
        else:
            print(f"No attributes found for Spatial ID: {spatial_id}, Zoom Level: {zoom_level}")
        
        # Test getting combined data
        print(f"\nRetrieving combined data for Spatial ID: {spatial_id}, Zoom Level: {zoom_level}")
        combined_data = mr_system.get_combined_mr_data(spatial_id, zoom_level)
        
        if combined_data:
            print("Successfully retrieved combined data:")
            # Convert geometry to string for display
            if combined_data["geometry"]:
                combined_data["geometry"] = str(combined_data["geometry"])
            print(json.dumps(combined_data, indent=2))
        else:
            print(f"No combined data found for Spatial ID: {spatial_id}, Zoom Level: {zoom_level}")
        
        # Test viewport data
        # Use spatial_ids that exist in the remote database
        viewport_ids = ["25/29/29801113/13210757", "25/30/29801116/13210732", "25/29/29801113/13210754", "nonexistent"]
        print(f"\nRetrieving viewport data for IDs: {viewport_ids}, Zoom Level: {zoom_level}")
        viewport_data = mr_system.get_viewport_data(viewport_ids, zoom_level)
        
        if viewport_data:
            print(f"Successfully retrieved viewport data for {len(viewport_data)} items:")
            for item in viewport_data:
                # Convert geometry to string for display
                if item["geometry"]:
                    item["geometry"] = str(item["geometry"])
                print(json.dumps(item, indent=2))
        else:
            print("No viewport data found")
        
        # Close database connections
        mr_system.close_connections()
        print("\nDatabase connections closed.")
        
    except Exception as e:
        print(f"Error testing MR authoring system: {e}")

if __name__ == "__main__":
    test_full_mr_system()