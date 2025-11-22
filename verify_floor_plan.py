import urllib.request
import json
import sys

BASE_URL = "http://localhost:8002/api/v1"
AUTH_URL = "http://localhost:8008/api/v1/auth/login"

def get_token():
    data = {"username": "admin", "password": "1234"}
    req = urllib.request.Request(
        AUTH_URL,
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result['access_token']
    except Exception as e:
        print(f"Login failed: {e}")
        sys.exit(1)

def verify_floor_plan():
    token = get_token()
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    # 1. Check/Create Room
    print("Checking/Creating Room...")
    room_name = "Terasz"
    room_id = None

    # Get all rooms
    req = urllib.request.Request(
        f"{BASE_URL}/rooms/",
        headers=headers,
        method='GET'
    )
    try:
        with urllib.request.urlopen(req) as response:
            rooms = json.loads(response.read().decode('utf-8'))
            for r in rooms:
                if r['name'] == room_name:
                    print(f"✅ Room '{room_name}' already exists: {r}")
                    room_id = r['id']
                    break
    except Exception as e:
        print(f"❌ Failed to get rooms: {e}")
        sys.exit(1)

    if not room_id:
        room_data = {
            "name": room_name,
            "width": 1000,
            "height": 800,
            "is_active": True
        }
        req = urllib.request.Request(
            f"{BASE_URL}/rooms/",
            data=json.dumps(room_data).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        try:
            with urllib.request.urlopen(req) as response:
                room = json.loads(response.read().decode('utf-8'))
                print(f"✅ Room created: {room}")
                room_id = room['id']
        except Exception as e:
            print(f"❌ Failed to create room: {e}")
            sys.exit(1)

    # 2. Create Table in Room
    print("\nCreating Table...")
    table_data = {
        "table_number": "T1",
        "room_id": room_id,
        "x": 100,
        "y": 100,
        "width": 80,
        "height": 80,
        "shape": "RECTANGLE",
        "capacity": 4
    }
    req = urllib.request.Request(
        f"{BASE_URL}/tables",
        data=json.dumps(table_data).encode('utf-8'),
        headers=headers,
        method='POST'
    )
    try:
        with urllib.request.urlopen(req) as response:
            table = json.loads(response.read().decode('utf-8'))
            print(f"✅ Table created: {table}")
    except Exception as e:
        print(f"❌ Failed to create table: {e}")
        # Read error body if possible
        if hasattr(e, 'read'):
            print(e.read().decode('utf-8'))
        sys.exit(1)

    print("\n✅ Floor Plan Backend Verification Successful!")

if __name__ == "__main__":
    verify_floor_plan()
