import http.client

conn = http.client.HTTPSConnection("api.piapi.ai")
payload = ''
headers = {
   'x-api-key': '00d821775c0ca4cd1691b8ef45ff5d388ccc1822d1e249e126455f75d6339e3b'
}
conn.request("GET", "/api/v1/task/", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))