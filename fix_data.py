import urllib.request
import json
import sys

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzYzNjk4ODQ0LCJleHAiOjE3NjM3MDI0NDQsInVzZXJuYW1lIjoiYWRtaW4iLCJyb2xlcyI6WyJBZG1pbiJdLCJwZXJtaXNzaW9ucyI6WyJvcmRlcnM6bWFuYWdlIiwiaW52ZW50b3J5OnZpZXciLCJudGFrOnNlbmQiLCJsb2dpc3RpY3M6bWFuYWdlIiwibWVudTp2aWV3IiwidmVoaWNsZXM6bWFuYWdlIiwib3JkZXJzOnZpZXciLCJyZXBvcnRzOm1hbmFnZSIsInJvbGVzOm1hbmFnZSIsImludmVudG9yeTptYW5hZ2UiLCJhc3NldHM6bWFuYWdlIiwiZW1wbG95ZWVzOm1hbmFnZSIsImZpbmFuY2U6bWFuYWdlIiwiYWRtaW46YWxsIiwibWVudTptYW5hZ2UiXX0.tnapAZA1EneWTKhP_uJhWJPiqtOR5nKc8qwbg9KM_t8"

def call_api(method, url, data=None):
    req = urllib.request.Request(url, method=method)
    req.add_header('Authorization', f'Bearer {TOKEN}')
    req.add_header('Content-Type', 'application/json')
    
    if data:
        json_data = json.dumps(data).encode('utf-8')
        req.data = json_data

    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status != 204:
                resp_data = json.loads(response.read().decode())
                print(f"{method} {url} - Status: {response.status}")
                # print(json.dumps(resp_data, indent=2))
                return resp_data
            else:
                print(f"{method} {url} - Status: 204")
                return None
    except urllib.error.HTTPError as e:
        print(f"{method} {url} - Error: {e.code} {e.reason}")
        print(e.read().decode())
        return None
    except Exception as e:
        print(f"{method} {url} - Failed: {str(e)}")
        return None

print("1. Checking Allergens...")
allergens = call_api("GET", "http://localhost:8001/api/v1/allergens")
allergen_id = None
if 'items' in allergens and len(allergens['items']) > 0:
    print(f"Found {len(allergens['items'])} allergens.")
    allergen_id = allergens['items'][0]['id']
else:
    print("Creating Allergen...")
    new_allergen = call_api("POST", "http://localhost:8001/api/v1/allergens", {"code": "GL", "name": "Glutén", "icon_url": "icon.png"})
    if new_allergen:
        allergen_id = new_allergen['id']

print(f"Allergen ID: {allergen_id}")

print("\n2. Updating Product Category...")
# Assuming Product ID 1 exists (verified previously)
call_api("PUT", "http://localhost:8001/api/v1/products/1", {"category_id": 1})

print("\n3. Linking Allergen to Product...")
if allergen_id:
    call_api("POST", "http://localhost:8001/api/v1/products/1/allergens", {"allergen_ids": [allergen_id]})

print("\n4. Final Verification...")
call_api("GET", "http://localhost:8001/api/v1/products/1")
