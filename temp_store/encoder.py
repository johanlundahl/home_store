from flask.json import JSONEncoder
from temp_store.model.sensor import Sensor
from datetime import datetime

class Encoder(JSONEncoder):
    
    def default(self, o):
        if any(type(o) is x for x in [Sensor]):
            return o.to_json()
        if type(o) is datetime:
        	return o.strftime('%Y-%m-%d %H:%M:%S')    
        return JSONEncoder.default(self, o)