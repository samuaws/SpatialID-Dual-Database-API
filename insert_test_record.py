import psycopg2
import json

def insert_test_record():
    try:
        # Connect to the database with the password we know works
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="spatial_attributes_db",
            user="postgres",
            password="admin"
        )
        
        # Create a cursor
        cursor = conn.cursor()
        
        # Create a test record
        test_attributes = {
            "name": "Test Location",
            "type": "point_of_interest",
            "description": "A test record for the MR authoring system",
            "annotations": [
                {
                    "type": "label",
                    "text": "Test Label",
                    "position": {"x": 10, "y": 20, "z": 0}
                },
                {
                    "type": "highlight",
                    "color": "#FF0000",
                    "opacity": 0.5
                }
            ]
        }
        
        # Insert the record
        cursor.execute("""
            INSERT INTO spatial_attributes (spatial_id, zoom_level, attributes)
            VALUES (%s, %s, %s)
            RETURNING id
        """, ('test123', 5, json.dumps(test_attributes)))
        
        # Get the inserted ID
        record_id = cursor.fetchone()[0]
        
        # Commit the transaction
        conn.commit()
        
        print(f"Successfully inserted test record with ID: {record_id}")
        
        # Now retrieve the record to verify
        cursor.execute("""
            SELECT id, spatial_id, zoom_level, attributes
            FROM spatial_attributes
            WHERE id = %s
        """, (record_id,))
        
        result = cursor.fetchone()
        if result:
            id, spatial_id, zoom_level, attributes = result
            print(f"\nRetrieved record:")
            print(f"ID: {id}")
            print(f"Spatial ID: {spatial_id}")
            print(f"Zoom Level: {zoom_level}")
            print(f"Attributes: {json.dumps(attributes, indent=2)}")
        else:
            print("Could not retrieve the inserted record.")
        
        # Close cursor and connection
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error inserting test record: {e}")

if __name__ == "__main__":
    insert_test_record()