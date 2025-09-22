# Database Schema Diagram

```
+---------------------+        +------------------------+
|   PostGIS DB        |        |  Attributes DB         |
| (spatial_id_db)     |        | (spatial_attributes_db)|
+---------------------+        +------------------------+
| Table: spatial_data |        | Table: spatial_attributes |
+---------------------+        +------------------------+
| - spatial_id        |<------>| - spatial_id           |
| - zoom_level        |<------>| - zoom_level           |
| - geometry          |        | - attributes (JSONB)   |
| - other fields...   |        | - created_at           |
|                     |        | - updated_at           |
+---------------------+        +------------------------+

                      Linked by spatial_id and zoom_level
```

## Query Flow

1. Application requests data for a specific Spatial ID and zoom level
2. System queries both databases in parallel:
   - PostGIS DB for geometry data
   - Attributes DB for additional metadata
3. Results are combined and returned to the application

## Data Flow for MR Authoring

```
+----------------+    Query     +-------------------+
|                |------------->| PostGIS DB        |
|                |              | (Spatial geometry) |
|                |<-------------|                   |
|                |   Geometry   +-------------------+
|                |
|  MR Authoring  |    Query     +-------------------+
|  Application   |------------->| Attributes DB     |
|                |              | (Custom metadata) |
|                |<-------------|                   |
|                |  Attributes  +-------------------+
|                |
|                |    Update    +-------------------+
|                |------------->| Attributes DB     |
|                |              | (Store new data)  |
+----------------+              +-------------------+
```

## Benefits of This Architecture

1. **Separation of Concerns**: Keeps spatial data separate from application-specific attributes
2. **Flexibility**: Different applications can have their own attribute schemas
3. **Performance**: Optimized queries for both spatial operations and attribute lookups
4. **Scalability**: Each database can be scaled independently based on usage patterns