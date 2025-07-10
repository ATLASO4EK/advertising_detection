import requests

url = 'http://127.0.0.1:5000/analyze'

with open('img.jpg', 'rb') as f:
    files = {'image': f}
    params = {"lat":"55.748613",
              "lon":"37.62651"}
    response = requests.get(url, files=files, data={}, params=params)


print("Response status code:", response.status_code)
print(response)