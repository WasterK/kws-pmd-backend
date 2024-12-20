from flask import Flask, request, jsonify
from flask_cors import CORS
from starlette.middleware.wsgi import WSGIMiddleware
import requests

app = Flask(__name__)
CORS(app)

# Example in-memory sites data
sites_data = [
    {
        "id": 1,
        "name": "AKAUTO",
        "location": "Moshi",
        "status": "active",
        "devices": [
            {
                "device_id": 101,
                "device_name": "PLD 1",
                "device_url" : 'https://pld1-akauto.kirankhairehomelab.online',
                "last_seen": "2024-11-15T10:00:00Z"
            },
            {
                "device_id": 102,
                "device_name": "PLD 2",
                "device_url" : 'https://pld2-akauto.kirankhairehomelab.online',
                "last_seen": "2024-11-14T14:30:00Z"
            },
            {
                "device_id": 103,
                "device_name": "PLD 3",
                "device_url" : 'https://pld3-akauto.kirankhairehomelab.online',
                "last_seen": "2024-11-13T18:00:00Z"
            }
        ],
        "created_at": "2024-11-01T12:00:00Z",
        "updated_at": "2024-11-15T10:05:00Z"
    },
    {
        "id": 2,
        "name": "AKAUTO",
        "location": "Chakan",
        "status": "inactive",
        "devices": [
            {
                "device_id": 103,
                "device_name": "Device 3",
                "status": "offline",
                "last_seen": "2024-11-12T09:30:00Z"
            }
        ],
        "created_at": "2024-10-20T08:00:00Z",
        "updated_at": "2024-11-12T09:45:00Z"
    }
]

DUMMY_DEVICE_DATA = {   101: {
                            "created_on": "2024-09-30 15:58:26",
                            "current_count": 354,
                            "location_id": 2,
                            "operation": "Punching",
                            "operator_name": "Robin",
                            "part_name": "Harness",
                            "part_number": "HS324",
                            "target": 7000,
                            "updated_on": "2024-11-24 13:44:05"
                        },
                        102: {
                            "created_on": "2024-09-30 15:58:26",
                            "current_count": 1668,
                            "location_id": 1,
                            "operation": "Assembly",
                            "operator_name": "John Doe",
                            "part_name": "Connector",
                            "part_number": "CN134",
                            "target": 10000,
                            "updated_on": "2024-11-24 13:44:05"
                        },
                        103: {
                            "created_on": "2024-09-30 15:58:26",
                            "current_count": 77,
                            "location_id": 10,
                            "operation": "Packing",
                            "operator_name": "Rakesh",
                            "part_name": "Asset Box",
                            "part_number": "KT245",
                            "target": 200,
                        }}

@app.route('/', methods=['GET'])
def home():
    return jsonify({'message': 'Welcome to PMD Backend API'})

@app.route('/api/sites', methods=['GET'])
def get_sites():
    return jsonify({'sites': sites_data})

@app.route('/api/sites/<int:site_id>', methods=['GET'])
def get_site(site_id):
    site = next((site for site in sites_data if site['id'] == site_id), None)
    if site:
        return jsonify(site)
    return jsonify({'error': 'Site not found'}), 404

@app.route('/api/sites/<int:site_id>/devices', methods=['GET'])
def get_devices_by_site(site_id):
    site = next((site for site in sites_data if site['id'] == site_id), None)
    if site:
        return jsonify({'devices': site['devices']})
    return jsonify({'error': 'Site not found'}), 404

@app.route('/api/sites/<int:site_id>/devices', methods=['POST'])
def add_device_to_site(site_id):
    site = next((site for site in sites_data if site['id'] == site_id), None)
    if site:
        new_device = request.json
        new_device['device_id'] = max(d['device_id'] for d in site['devices']) + 1 if site['devices'] else 1
        site['devices'].append(new_device)
        return jsonify(new_device), 201
    return jsonify({'error': 'Site not found'}), 404


@app.route('/api/device/<int:site_id>/<int:device_id>', methods=['GET'])
def get_device_data(site_id, device_id):
    for site in sites_data:
        if site.get('id') == site_id:
            for device in site.get('devices'):
                if device.get("device_id") == device_id:
                    try:
                        # Fetch data from the device
                        response = requests.get(url=f"{device.get('device_url')}/get-data/0")
                        response.raise_for_status()  # Raise an error for bad status codes
                        
                        device_data = response.json()

                        # device_data = DUMMY_DEVICE_DATA.get(device_id)
                        # if device_data:
                        #     device_data['device_id'] = device_id
                        #     device_data['site_id'] = site_id
                        # Return the fetched data
                        
                        return jsonify(device_data)  #device_data Assuming the device returns JSON
                    except requests.exceptions.RequestException as e:
                        # Handle request errors
                        return jsonify({
                            "status": "error",
                            "message": str(e)
                        }), 500
    
    # If no matching site or device is found
    return jsonify({
        "status": "error",
        "message": "Site or device not found"
    }), 404
    


app = WSGIMiddleware(app)