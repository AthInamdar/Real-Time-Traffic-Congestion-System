"""
Flask REST API - Serves traffic data to frontend with SSE support
"""
from flask import Flask, jsonify, render_template, Response
from pymongo import MongoClient
from bson import json_util
import json
import time
from datetime import datetime

app = Flask(__name__)

# MongoDB connection
mongo_client = MongoClient('mongodb://localhost:27017/')
db = mongo_client['TrafficDB']
collection = db['TrafficData']

# Track last sent row number for SSE
last_sent_row = 0
@app.route('/')
def index():
    """Serve the Leaflet.js map interface"""
    return render_template('index.html')

@app.route('/get_traffic', methods=['GET'])
def get_traffic():
    """
    API Endpoint: Returns latest traffic data
    Returns all records sorted by row_number for simulation
    """
    try:
        # Fetch all traffic data sorted by row number
        traffic_data = list(
            collection.find(
                {},
                {'_id': 0, 'location': 0}  # Exclude MongoDB _id and GeoJSON
            )
            .sort('row_number', 1)  # Sort by row number ascending
        )
        
        # Convert datetime objects to strings
        for record in traffic_data:
            if 'timestamp' in record:
                record['timestamp'] = record['timestamp'].isoformat()
        
        return jsonify({
            'success': True,
            'count': len(traffic_data),
            'data': traffic_data
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """
    API Endpoint: Returns traffic statistics
    """
    try:
        total_records = collection.count_documents({})
        congested_count = collection.count_documents({'status': 'Congested'})
        free_flow_count = collection.count_documents({'status': 'Free Flow'})
        
        # Get latest row number for simulation progress
        latest_record = collection.find_one({}, sort=[('row_number', -1)])
        latest_row = latest_record['row_number'] if latest_record else 0
        
        return jsonify({
            'success': True,
            'stats': {
                'total_records': total_records,
                'congested': congested_count,
                'free_flow': free_flow_count,
                'latest_row': latest_row
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/stream')
def stream():
    """
    Server-Sent Events endpoint for real-time data streaming
    """
    def event_stream():
        last_row = 0
        
        while True:
            try:
                # Find new records since last check
                new_records = list(
                    collection.find(
                        {'row_number': {'$gt': last_row}},
                        {'_id': 0, 'location': 0}
                    )
                    .sort('row_number', 1)
                    .limit(1)  # Get one record at a time
                )
                
                if new_records:
                    for record in new_records:
                        # Convert datetime to string
                        if 'timestamp' in record:
                            record['timestamp'] = record['timestamp'].isoformat()
                        
                        # Send as SSE
                        yield f"data: {json.dumps(record)}\n\n"
                        last_row = record['row_number']
                
                time.sleep(0.5)  # Check every 0.5 seconds
                
            except Exception as e:
                print(f"Stream error: {e}")
                time.sleep(1)
    
    return Response(
        event_stream(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive'
        }
    )

if __name__ == '__main__':
    print("🚀 Flask API server starting...")
    print("📍 Map Interface: http://localhost:5000")
    print("📊 API Endpoint: http://localhost:5000/get_traffic")
    app.run(debug=True, host='0.0.0.0', port=5000)