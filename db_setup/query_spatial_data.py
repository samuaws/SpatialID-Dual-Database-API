import psycopg2
import json

# Function to connect to the PostGIS database (using remote database)
def connect_to_postgis_db():
    try:
        conn = psycopg2.connect(
            host="1337.tlab.cloud",
            port="1337",
            database="spatial_id_db",
            user="postgres",
            password="tlab"
        )
        return conn
    except Exception as e:
        print(f"Error connecting to PostGIS database: {e}")
        return None

# Function to connect to the attributes database
def connect_to_attributes_db():
    try:
        conn = psycopg2.connect(
            host="localhost",  # Local PostgreSQL server
            port="5432",      # Default PostgreSQL port
            database="spatial_attributes_db",
            user="postgres",  # Default PostgreSQL username
            password="admin"  # Password we confirmed works
        )
        return conn
    except Exception as e:
        print(f"Error connecting to attributes database: {e}")
        return None

# Function to query spatial data from PostGIS
def query_postgis_data(spatial_id, zoom_level=None):
    conn = connect_to_postgis_db()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        
        # The remote database has bldg_spatial_ids table
        query = """SELECT geom, attributes, altitude FROM bldg_spatial_ids 
                  WHERE spatial_id = %s"""
        cursor.execute(query, (spatial_id,))
            
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            # Return a dictionary with all the data
            return {
                "geometry": result[0],  # geom
                "attributes": result[1],  # attributes (jsonb)
                "altitude": result[2]  # altitude
            }
        else:
            return None
    except Exception as e:
        print(f"Error querying PostGIS data: {e}")
        if conn:
            conn.close()
        return None

# Function to query attributes from the second database
def query_attributes_data(spatial_id, zoom_level):
    conn = connect_to_attributes_db()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        query = """SELECT attributes FROM spatial_attributes 
                  WHERE spatial_id = %s AND zoom_level = %s"""
        cursor.execute(query, (spatial_id, zoom_level))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            return result[0]  # Assuming attributes is the first column
        return None
    except Exception as e:
        print(f"Error querying attributes data: {e}")
        if conn:
            conn.close()
        return None

# Function to insert or update attributes in the second database
def update_attributes(spatial_id, zoom_level, attributes):
    conn = connect_to_attributes_db()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        query = """INSERT INTO spatial_attributes (spatial_id, zoom_level, attributes)
                  VALUES (%s, %s, %s)
                  ON CONFLICT (spatial_id, zoom_level) 
                  DO UPDATE SET attributes = %s, updated_at = CURRENT_TIMESTAMP"""
        cursor.execute(query, (spatial_id, zoom_level, json.dumps(attributes), json.dumps(attributes)))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating attributes: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

# Function to get combined data from both databases
def get_combined_data(spatial_id, zoom_level):
    postgis_data = query_postgis_data(spatial_id, zoom_level)
    attributes = query_attributes_data(spatial_id, zoom_level)
    
    result = {
        "spatial_id": spatial_id,
        "zoom_level": zoom_level,
        # Always prioritize attributes from the second database
        "attributes": attributes if attributes else (postgis_data.get("attributes") if postgis_data else None)
    }
    
    # Handle data from the remote database
    if postgis_data:
        result["geometry"] = postgis_data["geometry"]
        # Add altitude if available
        if "altitude" in postgis_data:
            result["altitude"] = postgis_data["altitude"]
    
    return result

# Example usage
def main():
    # Example spatial ID and zoom level
    spatial_id = "example_spatial_id"
    zoom_level = 10
    
    # Query combined data
    combined_data = get_combined_data(spatial_id, zoom_level)
    print("Combined data:")
    print(json.dumps(combined_data, indent=2))
    
    # Example: Update attributes for a spatial ID
    new_attributes = {
        "name": "Example Location",
        "type": "building",
        "height": 100,
        "color": "#FF5733",
        "custom_data": {
            "owner": "Company XYZ",
            "built_year": 2010
        }
    }
    
    success = update_attributes(spatial_id, zoom_level, new_attributes)
    if success:
        print(f"Successfully updated attributes for {spatial_id} at zoom level {zoom_level}")
    else:
        print(f"Failed to update attributes for {spatial_id} at zoom level {zoom_level}")
    
    # Query again to see the updated data
    updated_data = get_combined_data(spatial_id, zoom_level)
    print("\nUpdated combined data:")
    print(json.dumps(updated_data, indent=2))

if __name__ == "__main__":
    main()