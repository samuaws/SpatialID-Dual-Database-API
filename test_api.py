import requests
import json

# API base URL
BASE_URL = "http://localhost:5000"

def test_get_spatial_data():
    """Test the GET /api/spatial/<spatial_id> endpoint"""
    print("\n=== Testing GET /api/spatial/<spatial_id> endpoint ===")
    
    # Test with a valid spatial ID
    spatial_id = "25/29/29801113/13210757"
    response = requests.get(f"{BASE_URL}/api/spatial/{spatial_id}")
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("Response data:")
        print(json.dumps(data, indent=2))
    else:
        print(f"Error: {response.text}")
    
    # Test with an invalid spatial ID
    invalid_id = "invalid!id"
    response = requests.get(f"{BASE_URL}/api/spatial/{invalid_id}")
    
    print(f"\nInvalid ID test - Status Code: {response.status_code}")
    print(f"Error: {response.text}")

def test_update_attributes():
    """Test the POST /api/attributes/<spatial_id> endpoint"""
    print("\n=== Testing POST /api/attributes/<spatial_id> endpoint ===")
    
    # Test with a valid spatial ID and attributes
    spatial_id = "25/29/29801113/13210757"
    data = {
        "zoom_level": 5,  # Include zoom level as it's required
        "attributes": {
            "name": "Test Location",
            "description": "This is a test update",
            "test_value": 42
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/api/attributes/{spatial_id}",
        json=data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("Response data:")
        print(json.dumps(data, indent=2))
    else:
        print(f"Error: {response.text}")
    
    # Test with invalid data
    response = requests.post(
        f"{BASE_URL}/api/attributes/{spatial_id}",
        data="This is not valid JSON",
        headers={"Content-Type": "application/json"}
    )
    
    print(f"\nInvalid data test - Status Code: {response.status_code}")
    print(f"Error: {response.text}")

if __name__ == "__main__":
    print("Testing Spatial Data API endpoints...")
    
    # Test the root endpoint
    response = requests.get(BASE_URL)
    print(f"Root endpoint - Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    
    # Test the spatial data endpoint
    test_get_spatial_data()
    
    # Test the update attributes endpoint
    test_update_attributes()