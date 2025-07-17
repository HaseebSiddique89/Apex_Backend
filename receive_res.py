import http.client

conn = http.client.HTTPSConnection("api.piapi.ai")
payload = ''
headers = {
   'x-api-key': 'Enter_Your_API_KEY_Here'
}
conn.request("GET", "/api/v1/task/", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))
