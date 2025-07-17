import http.client
import json
import os
from dotenv import load_dotenv

load_dotenv()

conn = http.client.HTTPSConnection("api.piapi.ai")
payload = json.dumps({
   "model": "Qubico/trellis",
   "task_type": "image-to-3d",
   "input": {
      "prompt": "string",
      "ss_sampling_steps": 50,
      "slat_sampling_steps": 50,
      "ss_guidance_strength": 7.5,
      "slat_guidance_strength": 3.0,
      "seed": 0
   },
   "config": {
      "webhook_config": {
         "endpoint": "string",
         "secret": "string"
      }
   }
})
headers = {
   'x-api-key': os.getenv("PIAPI_API_KEY"),
   'Content-Type': 'application/json'
}
conn.request("POST", "/api/v1/task", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))
