from flask import Flask, request, jsonify
import json
import re
import logging
from functools import wraps
from db_setup.query_spatial_data import query_postgis_data, query_attributes_data, update_attributes, get_combined_data

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Validation functions
def validate_spatial_id(spatial_id):
    """Validate spatial ID format"""
    # Allow slashes for hierarchical IDs like '25/29/29801113/13210757'
    pattern = r'^[A-Za-z0-9_/.-]+$'
    return bool(re.match(pattern, spatial_id))

# Decorator for validating spatial ID
def require_valid_spatial_id(f):
    @wraps(f)
    def decorated_function(spatial_id, *args, **kwargs):
        if not validate_spatial_id(spatial_id):
            return jsonify({"error": "Invalid spatial ID format"}), 400
        return f(spatial_id, *args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return jsonify({
        "message": "Spatial Data API",
        "endpoints": {
            "/api/spatial/<spatial_id>": "Get spatial data by ID",
            "/api/attributes/<spatial_id>": "Update attributes for a spatial ID (POST)"
        }
    })

# Basic error handler
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error"}), 500

@app.route('/api/spatial/<path:spatial_id>', methods=['GET'])
@require_valid_spatial_id
def get_spatial_data(spatial_id):
    """Get spatial data by ID from both databases"""
    try:
        # Get zoom level from query parameters, default to 25 if not provided
        zoom_level = request.args.get('zoom_level', default=25, type=int)
        
        # Use the get_combined_data function to get data from both databases
        result = get_combined_data(spatial_id, zoom_level)
        
        if not result:
            return jsonify({"error": "Spatial ID not found"}), 404
            
        if not result.get('geometry'):
            return jsonify({"error": "No geometry data found for this spatial ID"}), 404
            
        return jsonify({
            "spatial_id": spatial_id,
            "zoom_level": zoom_level,
            "geometry": result.get("geometry"),
            "attributes": result.get("attributes"),
            "altitude": result.get("altitude")
        })
    except Exception as e:
        app.logger.error(f"Error retrieving spatial data: {str(e)}")
        return jsonify({"error": "Internal server error while retrieving spatial data"}), 500

@app.route('/api/attributes/<path:spatial_id>', methods=['POST'])
@require_valid_spatial_id
def update_spatial_attributes(spatial_id):
    """Update attributes for a spatial ID"""
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Missing JSON data in request"}), 400
            
        if not isinstance(data, dict):
            return jsonify({"error": "Invalid JSON format, expected an object"}), 400
    except Exception as e:
        app.logger.error(f"Error parsing JSON: {str(e)}")
        return jsonify({"error": "Invalid JSON format in request"}), 400
        
    try:
        
        # Extract zoom_level and attributes from request data
        zoom_level = data.get('zoom_level')
        attributes = data.get('attributes')
        
        if zoom_level is None:
            return jsonify({"error": "Missing required 'zoom_level' parameter"}), 400
            
        if not attributes or not isinstance(attributes, dict):
            return jsonify({"error": "Missing or invalid 'attributes' parameter"}), 400
        
        # Check if spatial ID exists before updating
        existing_data = get_combined_data(spatial_id, zoom_level)
        if not existing_data:
            return jsonify({"error": f"Spatial ID '{spatial_id}' not found"}), 404
            
        # Update attributes using the update_attributes function
        success = update_attributes(spatial_id, zoom_level, attributes)
        
        if not success:
            return jsonify({"error": "Failed to update attributes in database"}), 500
            
        # Get the updated data to return
        updated_data = get_combined_data(spatial_id, zoom_level)  # Pass the same zoom_level used for update
        
        return jsonify({
            "message": "Attributes updated successfully",
            "spatial_id": spatial_id,
            "updated_attributes": updated_data.get("attributes")
        })
    except ValueError as e:
        return jsonify({"error": f"Invalid data format: {str(e)}"}), 400
    except Exception as e:
        app.logger.error(f"Error updating attributes: {str(e)}")
        return jsonify({"error": "Internal server error while updating attributes"}), 500

# Global error handler for unexpected exceptions
@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {str(e)}")
    return jsonify({
        "error": "An unexpected error occurred",
        "details": str(e) if app.debug else "Contact administrator for details"
    }), 500

if __name__ == '__main__':
    logger.info("Starting Spatial Data API on port 5000")
    logger.info("Available endpoints:")
    logger.info("  - GET  /api/spatial/<spatial_id>: Get spatial data by ID")
    logger.info("  - POST /api/attributes/<spatial_id>: Update attributes for a spatial ID")
    app.run(debug=True, port=5000)