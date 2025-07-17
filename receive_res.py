import http.client
import os
from dotenv import load_dotenv

load_dotenv()

conn = http.client.HTTPSConnection("api.piapi.ai")
payload = ''
headers = {
   'x-api-key': os.getenv("PIAPI_API_KEY")
}
conn.request("GET", "/api/v1/task/", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))
