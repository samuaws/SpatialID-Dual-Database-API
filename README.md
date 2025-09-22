# Spatial ID Database Integration

This project demonstrates how to integrate a secondary database with the PostGIS database, using Spatial ID as the linking key. The setup allows querying both databases to retrieve combined spatial and attribute data.

## Overview

The system consists of two databases (both now running locally):

1. **PostGIS Database** (Mock Local Version)
   - Host: localhost
   - Port: 5432
   - Database: spatial_attributes_db
   - Contains spatial geometry data indexed by Spatial ID
   - Note: Originally designed to connect to a remote server (1337.tlab.cloud:1337) but now using a local mock version due to connectivity issues

2. **Attributes Database** (Local)
   - Host: localhost
   - Port: 5432
   - Database: spatial_attributes_db (same database as above)
   - Contains additional attributes and metadata linked to Spatial IDs
   - Allows for extending the spatial data with application-specific information

## Setup Instructions

### 1. Create the Database

Run the SQL scripts to create the database and required tables:

```bash
psql -U postgres -c "CREATE DATABASE spatial_attributes_db;"
psql -U postgres -d spatial_attributes_db -f db_setup/setup_second_db.sql
psql -U postgres -d spatial_attributes_db -f add_unique_constraint.sql
psql -U postgres -d spatial_attributes_db -c "CREATE EXTENSION IF NOT EXISTS postgis;"
psql -U postgres -d spatial_attributes_db -f create_mock_postgis_table.sql
```

These scripts will:
- Create a new database called `spatial_attributes_db`
- Create a table for storing attributes linked to Spatial IDs
- Set up necessary indexes for efficient querying
- Create functions for querying combined data and updating attributes
- Add a unique constraint on spatial_id and zoom_level for upsert operations
- Install the PostGIS extension for spatial data support
- Create a mock spatial_data table to simulate the PostGIS database

### 2. Configure Connection Settings

Update the connection settings in `db_setup/query_spatial_data.py` to match your local PostgreSQL configuration:

```python
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
```

### 3. Testing the System

Two test scripts are provided to verify the system functionality:

1. **Test MR Authoring System**
   ```bash
   python test_mr_authoring.py
   ```
   This script tests the basic MR authoring functionality with the attributes database.

2. **Test Full MR System**
   ```bash
   python test_full_mr_system.py
   ```
   This script tests the complete system, including both spatial data and attributes retrieval.

## Usage

### Querying Combined Data

Use the Python script to query data from both databases:

```bash
python db_setup/query_spatial_data.py
```

The script demonstrates:
1. Connecting to both databases
2. Querying spatial data from PostGIS using Spatial ID
3. Querying attributes from the secondary database using the same Spatial ID
4. Combining the results into a unified response
5. Updating attributes for a specific Spatial ID

### Database Schema

#### Spatial Attributes Table

```sql
CREATE TABLE spatial_attributes (
    id SERIAL PRIMARY KEY,
    spatial_id VARCHAR(255) NOT NULL,
    zoom_level INTEGER NOT NULL,
    attributes JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Indexes

```sql
CREATE INDEX idx_spatial_id ON spatial_attributes(spatial_id);
CREATE INDEX idx_zoom_level ON spatial_attributes(zoom_level);
CREATE INDEX idx_spatial_id_zoom ON spatial_attributes(spatial_id, zoom_level);
```

## Integration with MR Authoring

For MR Authoring applications, you can:

1. Store application-specific data in the attributes database
2. Query both databases when rendering MR content
3. Update attributes as users interact with the MR environment

This approach keeps the spatial data in PostGIS while allowing flexible extension with application-specific attributes in the secondary database.

## Requirements

- PostgreSQL with PostGIS extension
- Python 3.x
- psycopg2 Python package (`pip install psycopg2-binary`)