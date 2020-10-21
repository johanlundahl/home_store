# Home Store
This project stores sensor reading values to a database. Other components can interact with this component through REST endpoints.

This project is suitable to run on a Raspberry Pi and is intended to use with [Home Monitor](http://github.com/johanlundahl/home_monitor), [Temp Sensor](http://github.com/johanlundahl/temp_sensor), [Home Eye](http://github.com/johanlundahl/home_eye) and [Mosquitto MQTT Broker](https://randomnerdtutorials.com/how-to-install-mosquitto-broker-on-raspberry-pi/).

## Installation

Clone this git repo

```
$ git clone https://github.com/johanlundahl/home_store
```

Requires python 3.6 or above. Install required python modules

```
$ sudo pip3 install -r requirements.txt
```

Create the database 
```
$ python3 -m home_store.cmdtool init
```

## Running
Run the application using
```
$ python3 -m home_store.app
```

## Logging
Application events are logged to the application log file and can be viewed through
```
$ tail -f application.log
```

## Database functionality
Use the cmdtool to setup, clean or drop the database. It can also help you simulate database entries for testing. Se the complete list of functionality by entering
```
$ python3 -m home_store.cmdtool -h
``` 


## How to use the application
The application exposes http endpoint to interact with. The web application runs on port 5000 by default and has the endpoints listed below.

### List sensors
Use the following to get a list of all sensors:
```
GET /api/sensors HTTP/1.1
```

### Add sensor value
Use the following to add a new sensor value:
```
POST /api/sensors HTTP/1.1
{
	"name": "basement",
	"temperature": 18,
	"humidity": 55,
	"timestamp": "2019-09-04 21:10:03"
}
```

### Get sensor values
Use the following to get sensor values for a sensor:
```
GET /api/sensors/<name> HTTP/1.1
```
By default the 20 latest sensor values are returned, i.e. the same as `offset=0&limit=20`.

The following attributes are available:
* `offset=[int]` use together with limit to paginate the results.
* `limit=[int]` use together with offset to paginate the results.
* `date=[string]` will filter the result to include values from the given date in the format `2019-12-27`
* `timestamp=[string]` will filter the result to include values that matches the given datetime in the format `2019-12-27 18:05:22`
* `sort=[asc|desc]` will order the result ascending or descending based on timestamp

Both the `date` and the `timestamp` attributes can have an operator added to it. The valid operators are `qe`, `gt`, `ge`, `lt`, `te`. The following filters all sensor values newer than 2019-12-27:
```
GET /api/sensors/<name>?date[gt]=2019-12-27 HTTP/1.1
``` 

### Get latest sensor value
Use the following to get the latest sensor value for <name> as per its datetime attribute:
```
GET /api/sensors/<name>/latest HTTP/1.1
```

### Get sensor history
This endpoint will return historical sensor values. Use the `to` and `from` attributes to specify the time period. 
```
GET /api/sensors/<name>/history HTTP/1.1 
```

The following attributes are available:
* `to=[string]` the end time in the format `2020-02-05 12:30:00`.
* `from=[string]` the start time in the format `2020-02-01 23:15:30`.
* `resolution=[int]` will reduce the number of sensor values to the specified value. The resulting values are scattered over the given date interval.
