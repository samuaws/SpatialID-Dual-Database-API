import requests
import json
from db_setup.query_spatial_data import update_attributes, get_combined_data

# API base URL
BASE_URL = "http://localhost:5000"

def test_attributes_priority():
    """Test that attributes from the second database are prioritized"""
    print("\n=== Testing Attributes Priority ===\n")
    
    # Use a valid spatial ID from our tests
    spatial_id = "25/29/29801113/13210757"
    zoom_level = 5
    
    # First, check what's in the PostGIS database
    print("1. Getting initial data from API...")
    response = requests.get(f"{BASE_URL}/api/spatial/{spatial_id}")
    initial_data = response.json()
    print(f"Initial attributes: {json.dumps(initial_data.get('attributes', {}), indent=2)}")
    
    # Now update attributes in the second database
    print("\n2. Updating attributes in the second database...")
    new_attributes = {
        "name": "Test Building",
        "description": "This is a test building with custom attributes",
        "height": 42,
        "test_value": True
    }
    
    success = update_attributes(spatial_id, zoom_level, new_attributes)
    if success:
        print(f"Successfully updated attributes for {spatial_id} at zoom level {zoom_level}")
    else:
        print(f"Failed to update attributes for {spatial_id} at zoom level {zoom_level}")
    
    # Now get the data again from the API
    print("\n3. Getting updated data from API...")
    response = requests.get(f"{BASE_URL}/api/spatial/{spatial_id}?zoom_level={zoom_level}")
    updated_data = response.json()
    print(f"Updated attributes: {json.dumps(updated_data.get('attributes', {}), indent=2)}")
    
    # Check if the attributes match what we set
    print("\n4. Verifying attributes priority:")
    api_attributes = updated_data.get('attributes', {})
    
    if not api_attributes:
        print("❌ No attributes returned from API")
        return
    
    # Check if our custom attributes are present
    matches = True
    for key, value in new_attributes.items():
        if key not in api_attributes or api_attributes[key] != value:
            matches = False
            break
    
    if matches:
        print("✅ Success! API is returning attributes from the second database")
    else:
        print("❌ API is not returning the expected attributes from the second database")
        print(f"Expected: {json.dumps(new_attributes, indent=2)}")
        print(f"Got: {json.dumps(api_attributes, indent=2)}")

if __name__ == "__main__":
    test_attributes_priority()