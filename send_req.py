import http.client
import json

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
   'x-api-key': '00d821775c0ca4cd1691b8ef45ff5d388ccc1822d1e249e126455f75d6339e3b',
   'Content-Type': 'application/json'
}
conn.request("POST", "/api/v1/task", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))