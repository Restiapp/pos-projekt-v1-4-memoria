import urllib.request
import json
import sys

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzYzNjk4ODQ0LCJleHAiOjE3NjM3MDI0NDQsInVzZXJuYW1lIjoiYWRtaW4iLCJyb2xlcyI6WyJBZG1pbiJdLCJwZXJtaXNzaW9ucyI6WyJvcmRlcnM6bWFuYWdlIiwiaW52ZW50b3J5OnZpZXciLCJudGFrOnNlbmQiLCJsb2dpc3RpY3M6bWFuYWdlIiwibWVudTp2aWV3IiwidmVoaWNsZXM6bWFuYWdlIiwib3JkZXJzOnZpZXciLCJyZXBvcnRzOm1hbmFnZSIsInJvbGVzOm1hbmFnZSIsImludmVudG9yeTptYW5hZ2UiLCJhc3NldHM6bWFuYWdlIiwiZW1wbG95ZWVzOm1hbmFnZSIsImZpbmFuY2U6bWFuYWdlIiwiYWRtaW46YWxsIiwibWVudTptYW5hZ2UiXX0.tnapAZA1EneWTKhP_uJhWJPiqtOR5nKc8qwbg9KM_t8"

def check_url(url):
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {TOKEN}')
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            print(f"GET {url} - Status: {response.status}")
            print(json.dumps(data, indent=2))
    except urllib.error.HTTPError as e:
        print(f"GET {url} - Error: {e.code} {e.reason}")
        print(e.read().decode())
    except Exception as e:
        print(f"GET {url} - Failed: {str(e)}")

print("Verifying API Data...")
check_url("http://localhost:8001/api/v1/categories")
check_url("http://localhost:8001/api/v1/products")
