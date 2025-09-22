import sys
import os
import json

# Add the db_setup directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'db_setup'))

# Import the functions from query_spatial_data.py
from db_setup.query_spatial_data import connect_to_postgis_db, query_postgis_data, get_combined_data

def test_remote_connection():
    print("Testing connection to remote PostGIS database...")
    
    # Test connection
    conn = connect_to_postgis_db()
    if not conn:
        print("Failed to connect to database.")
        return
    
    # Check which database we're connected to
    cursor = conn.cursor()
    cursor.execute("SELECT current_database()")
    current_db = cursor.fetchone()[0]
    print(f"Connected to database: {current_db}")
    
    # Close the connection
    cursor.close()
    conn.close()
    
    # Test querying data
    print("\nTesting query for spatial data...")
    # Use one of the spatial_ids we saw in the database
    spatial_id = "25/29/29801113/13210757"
    
    # Query the data
    data = query_postgis_data(spatial_id)
    
    if data:
        print(f"Successfully retrieved data for spatial_id: {spatial_id}")
        print("Data type:", type(data))
        print("Data contents:")
        if isinstance(data, dict):
            for key, value in data.items():
                print(f"  {key}: {type(value)}")
                if key == "attributes" and value:
                    print(f"    {value}")
        else:
            print(f"  {data}")
    else:
        print(f"No data found for spatial_id: {spatial_id}")

if __name__ == "__main__":
    test_remote_connection()