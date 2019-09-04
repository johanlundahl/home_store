from flask.json import JSONEncoder
from temp_store.model.sensor import Sensor

class Encoder(JSONEncoder):
    
    def default(self, o):
        if any(type(o) is x for x in [Sensor]):
            return o.to_json()
        return JSONEncoder.default(self, o)