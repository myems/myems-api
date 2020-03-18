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
[User](#markdown-header-user)


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
$ curl -i -H "Content-Type: application/json" -X PUT -d '{"data":{"name":"johnson", "display_name":"约翰逊", "email":"johnson@myems.io"}}' http://BASE_URL/users/{id}
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