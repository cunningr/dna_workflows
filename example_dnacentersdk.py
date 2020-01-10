import json
from dnacentersdk import DNACenterAPI

api = DNACenterAPI(username='devnetuser', password='Cisco123!', base_url="https://sandboxdnac2.cisco.com:443", version='1.3.0')

devices = api.devices.get_device_list()



print(devices)

# Dump to JSON
# print(json.dumps(devices, indent=4))
