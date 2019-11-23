# home_store
This project stores sensor reading values to a database. Other components can interact with this component through REST endpoints.


## Installation

Clone this git repo

```
$ git clone https://github.com/johanlundahl/home_store
```


## Requirements
Install required python modules

```
$ sudo pip install -r requirements.txt
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

Use the following to get a list of all sensors:
```
GET /api/sensors HTTP/1.1
```

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

Use the following to get sensor values for a sensor:
```
GET /api/sensors/basement HTTP/1.1
```