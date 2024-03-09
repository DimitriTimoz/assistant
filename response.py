
import datetime
import json

current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

response = {
    "time": current_time
}

json_response = json.dumps(response)
print(json_response)
