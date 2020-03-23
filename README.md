# MyEMS API Service

## Introduction
Providing REST API service for MyEMS Web APP, Android APP and iOS APP and/or third parties


## Prerequisites
simplejson
mysql.connector
falcon
falcon_cors
gunicorn


## Installation

* Install simplejson
```
$ cd ~/tools
$ git clone https://github.com/simplejson/simplejson.git
$ cd simplejson
$ sudo python3 setup.py install 
```

* Install Falcon,
  if you are behind proxy, use --proxy parameter
  Refer to https://falconframework.org/
           https://github.com/lwcolton/falcon-cors
           https://github.com/yohanboniface/falcon-multipart
```
  $ mkdir ~/tools/falcon && cd ~/tools/falcon
  $ pip3 download cython falcon falcon-cors falcon-multipart
  $ export LC_ALL="en_US.UTF-8"
  $ export LC_CTYPE="en_US.UTF-8"
  $ sudo dpkg-reconfigure locales
  $ sudo pip3 install --upgrade --no-index --find-links ~/tools/falcon cython falcon falcon-cors falcon-multipart
```

* Install gunicorn, refer to http://gunicorn.org
```
  $ mkdir ~/tools/gunicorn && cd ~/tools/gunicorn
  $ pip3 download gunicorn
  $ sudo pip3 install --no-index --find-links ~/tools/gunicorn gunicorn
```

* Install gunicorn service for myems-api:
```
  $ cd ~/myems-api
  $ sudo cp -R ~/myems-api /myems-api
```
  Check and change the config file if necessary:
```
  $ sudo nano /myems-api/config.py
```
   Change the listening port (8080 as an example) in gunicorn.socket:
```
   $ sudo nano /myems-api/gunicorn.socket
ListenStream=0.0.0.0:8080
    $ sudo ufw allow 8080
```
   Setup systemd configure files:
```
   $ sudo cp /myems-api/gunicorn.service /lib/systemd/system/
   $ sudo cp /myems-api/gunicorn.socket /lib/systemd/system/
   $ sudo cp /myems-api/gunicorn.conf /usr/lib/tmpfiles.d/
```
   Next enable the services so they autostart at boot:
```
   $ sudo systemctl enable gunicorn.service
   $ sudo systemctl enable gunicorn.socket
```

## Run for debugging and testing
```
$ cd myems-api
$ sudo gunicorn -b 127.0.0.1:8080 app:api
```

## API List
[Data Source](#Data-Source) | [Point](#Point)

[User](#User) | [Privilege](#Privilege)


### Data Source
* GET Data Source by ID

Result in JSON

| Name          | Data Type | Description                               |
|---------------|-----------|-------------------------------------------|
| id            | integer   | Complex ID                                |
| name          | string    | Complex name                              |
| uuid          | string    | Complex UUID                              |
| protocol      | string    | Protocol Type Supported: bacnet-ip, modbus-tcp, s7, opc-ua, control-logix, |
| connection    | json      | Connection data in JSON. BACnet/IP example: {"host":"10.1.2.88"}, Modbus TCP example: {"host":"10.1.2.88", "port":502}, S7 example: {"host":"10.1.2.202", "port":102, "rack": 0, "slot": 2}, ControlLogix example: {"host":"10.1.2.88","port":44818,"processorslot":3} OPC UA example: {"url":"opc.tcp://10.1.2.5:49320/OPCUA/SimulationServer/"} |

```bash
$ curl -i -X GET http://BASE_URL/datasources/{id}
```
* GET all Data Sources
```bash
$ curl -i -X GET http://BASE_URL/datasources
```
* DELETE Data Source by ID
```bash
$ curl -i -X DELETE http://BASE_URL/datasources/{id}
```
* POST Data Source
```bash
$ curl -i -H "Content-Type: application/json" -X POST -d '{"data":{"name":"Modbus1", "protocol":"modbus-tcp", "connection":"{\"host\":\"10.1.2.88\", \"port\":502}"}}' http://BASE_URL/datasources
```
* PUT Data Source
```bash
$ curl -i -H "Content-Type: application/json" -X PUT -d '{"data":{"name":"Modbus1", "protocol":"modbus-tcp", "connection":"{\"host\":\"10.1.2.99\", \"port\":502}"}}' http://BASE_URL/datasources/{id}
```
* GET all points of the Data Source by ID
```bash
$ curl -i -X GET http://BASE_URL/datasources/{id}/points
```

### Privilege
* GET Privilege by ID
```bash
$ curl -i -X GET http://BASE_URL/privileges/{id}
```
* GET All Privileges
```bash
$ curl -i -X GET http://BASE_URL/privileges
```
* DELETE Privilege by ID
```bash
$ curl -i -X DELETE http://BASE_URL/privileges/{id}
```
* POST New Privilege
```bash
$ curl -i -H "Content-Type: application/json" -X POST -d '{"data":{"name":"superusers","data":"{\"spaces\":[1,2,3,5]}"}}' http://BASE_URL/privileges
```
* PUT Privilege
```bash
$ curl -i -H "Content-Type: application/json" -X PUT -d '{"data":{"name":"superusers", "data":"{\"spaces\":[1, 3]}"}}' http://BASE_URL/privileges/{id}
```



### Point

* GET Point by ID

Response Result

| Name          | Data Type | Description                               |
|---------------|-----------|-------------------------------------------|
| id            | integer   | Point ID                                  |
| name          | string    | Point name                                |
| data_source_id| integer   | Data Source ID                            |
| object_type   | string    | Object Type ('ENERGY_VALUE', 'ANALOG_VALUE, 'BINARY_VALUE')   |
| units         | string    | Units of Measure                          |
| low_limit     | float     | Low Limit of the Point Value              |
| hi_limit      | float     | High Limit of the Point Value             |
| is_trend      | boolean   | The Point Value is Recorded as Trend      |
| address       | json      | Address structure varied by protocol      |
|               |           | Modbus TCP Structure                      |
| ├slave_id     | integer   | Slave ID                                  |
| ├function_code| integer   | Modbus functions:READ_COILS = 1, READ_DISCRETE_INPUTS = 2, READ_HOLDING_REGISTERS = 3, READ_INPUT_REGISTERS = 4    |
| ├offset       | integer   | Offset                                    |
| ├number_of_registers  | integer   | Number of Registers               |
| └format       | string    | Data Format. see below introductions      |
|               |           | ControlLogix Structure                    |
| ├data_type    | string    | 'REAL', 'DINT', 'STRING'                  |
| └tag          | string    | Tag Name                                  |
|               |           | BACnet/IP Structure                       |
| ├object_type  | string    | BACnet Object Type ('analogValue', 'analogInput', 'analogOutput', 'binaryValue', 'binaryInput', 'binaryOutput')|
| ├object_id    | integer   | BACnet Object Instance Number             |
| ├property_name| string    | BACnet Property Name ('presentValue')     |
| └property_array_index| integer/null    | BACnet Property Array Index or None of Object Type is not Array   |


```bash
$ curl -i -X GET http://BASE_URL/points/{id}
```
* GET all Points
```bash
$ curl -i -X GET http://BASE_URL/points
```
* DELETE Point by ID
```bash
$ curl -i -X DELETE http://BASE_URL/points/{id}
```
* POST Point
```bash
$ curl -i -H "Content-Type: application/json" -X POST -d '{"data":{"name":"ModbusPoint1", "data_source_id":1, "object_type": "ENERGY_VALUE", "units":"kWh", "low_limit":0, "hi_limit":999999999, "is_trend":true, "address":"{\"slave_id\":1, \"function_code\":3, \"offset\":1, \"number_of_registers\":2, \"data_format\":\"float\"}"}}' http://BASE_URL/points
```
* PUT Point
```bash
$ curl -i -H "Content-Type: application/json" -X PUT -d '{"data":{"name":"ModbusPoint1", "data_source_id":1, "object_type": "ENERGY_VALUE", "units":"kWh", "low_limit":0, "hi_limit":999999999, "is_trend":true, "address":"{\"slave_id\":1, \"function_code\":3, \"offset\":1, \"number_of_registers\":2, \"data_format\":\"float\"}"}}' http://BASE_URL/points/{id}
```


### User
* GET User by ID
```bash
$ curl -i -X GET http://BASE_URL/users/{id}
```
* GET All Users
```bash
$ curl -i -X GET http://BASE_URL/users
```
* DELETE User by id
```bash
$ curl -i -X DELETE http://BASE_URL/users/{id}
```
* POST New User
```bash
$ curl -i -H "Content-Type: application/json" -X POST -d '{"data":{"name":"johnson", "display_name":"约翰逊", "email":"johnson@myems.io", "is_admin":true, password":"Thi$Pa$$w0rd"}}' http://BASE_URL/users
```
* PUT User Profile
```bash
$ curl -i -H "Content-Type: application/json" -X PUT -d '{"data":{"name":"johnson", "display_name":"约翰逊", "is_admin":true, "email":"johnson@myems.io"}}' http://BASE_URL/users/{id}
```
* PUT User Login
```bash
$ curl -i -H "Content-Type: application/json" -X PUT -d '{"data":{"username":"johnson", "password":"!Password1"}}' http://BASE_URL/users/login
```
* PUT User Logout
```bash
$ curl -i -H "Content-Type: application/json" -X PUT --cookie "user_uuid=793f1bb4-6e25-4242-8cdc-2f662b25484f;token=a6e52af82e5b4168ae03b1c5fd8fa31b2ab3a338" http://BASE_URL/users/logout
```
* PUT User change password
```bash
$ curl -i -H "Content-Type: application/json" -X PUT -d '{"data":{"password":"NewPassword1"}}' --cookie "user_uuid=793f1bb4-6e25-4242-8cdc-2f662b25484f;token=a6e52af82e5b4168ae03b1c5fd8fa31b2ab3a338" http://BASE_URL/users/changepassword
```
* PUT User reset any user's password called by administrator
```bash
$ curl -i -H "Content-Type: application/json" -X PUT -d '{"data":{"name":"johnson","password":"NewPassword1"}}' --cookie "user_uuid=793f1bb4-6e25-4242-8cdc-2f662b25484f;token=a6e52af82e5b4168ae03b1c5fd8fa31b2ab3a338" http://BASE_URL/users/resetpassword
```

