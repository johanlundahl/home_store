# Home Store
This project stores sensor reading values to a database. Other components can interact with this component through REST endpoints.


## Installation

Clone this git repo

```
$ git clone https://github.com/johanlundahl/home_store
```


## Requirements
Requires python 3.6 or above. Install required python modules

```
$ sudo pip3 install -r requirements.txt
```

Create the database 
```
$ python3 -m home_store.db -create
```


## Running
Run the application using
```
$ python3 -m home_store.app
```

## How to use the application
The application exposes http endpoint to interact with. The web application runs on port 5000 by default.

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
Use any of the following to get sensor values for a sensor:
```
GET /api/sensors/<name> HTTP/1.1
```

The following attributes are available:
`page=[int]` use together with size to paginate the results. First page should be 1
`size=[int]` use together with page to paginate the results.
`date`=[string] will filter the result to include values from this date


### Get latest sensor value
```
GET /api/sensors/<name>/latest HTTP/1.1 - returns the latest sensor value for <name>
```

### Get sensor trend

```
GET /api/sensors/<name>/trend HTTP/1.1 - returns one sensor value per hour for the last two days for <name>
