import psycopg2

def examine_postgis_schema():
    try:
        # Connect to the PostGIS database
        conn = psycopg2.connect(
            host="1337.tlab.cloud",
            port="1337",
            database="spatial_id_db",
            user="postgres",
            password="tlab"
        )
        
        # Create a cursor
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cursor.fetchall()
        
        print("Tables in the PostGIS database:")
        for table in tables:
            table_name = table[0]
            print(f"\n{'-'*50}\nTable: {table_name}")
            
            # Get column information for each table
            cursor.execute(f"""
                SELECT column_name, data_type, character_maximum_length
                FROM information_schema.columns
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position
            """)
            columns = cursor.fetchall()
            
            print("Columns:")
            for column in columns:
                col_name, data_type, max_length = column
                length_info = f"({max_length})" if max_length else ""
                print(f"  - {col_name}: {data_type}{length_info}")
            
            # Get primary key information
            cursor.execute(f"""
                SELECT c.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.constraint_column_usage AS ccu USING (constraint_schema, constraint_name)
                JOIN information_schema.columns AS c ON c.table_schema = tc.constraint_schema
                    AND tc.table_name = c.table_name AND ccu.column_name = c.column_name
                WHERE constraint_type = 'PRIMARY KEY' AND tc.table_name = '{table_name}'
            """)
            pks = cursor.fetchall()
            
            if pks:
                print("Primary Keys:")
                for pk in pks:
                    print(f"  - {pk[0]}")
            
            # Get index information
            cursor.execute(f"""
                SELECT indexname, indexdef
                FROM pg_indexes
                WHERE tablename = '{table_name}'
            """)
            indexes = cursor.fetchall()
            
            if indexes:
                print("Indexes:")
                for idx in indexes:
                    idx_name, idx_def = idx
                    print(f"  - {idx_name}: {idx_def}")
        
        # Close cursor and connection
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error examining PostGIS schema: {e}")

if __name__ == "__main__":
    examine_postgis_schema()