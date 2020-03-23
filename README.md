# MyEMS API Service

## Introduction
Providing REST API service for MyEMS Web APP, Android APP and iOS APP and/or third parties


## Prerequisites
mysql.connector
gunicorn
falcon
falcon_cors


## Installation


## Run for Testing
```
$ cd feed-rest-api
$ sudo gunicorn -b 127.0.0.1:8080 app:api
```

## API List
[Data Source](#Data-Source)
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