import json
import datetime
import base64
import os
from botocore.vendored import requests

USERNAME = os.environ['USERNAME']
PASSWORD = os.environ['PASSWORD']

cache = {"valid": False,
         "cars": 0,
         "last_update": datetime.datetime.now(),
         "token_exp": datetime.datetime.now(),
         "token": ""
         }

def get_cars_from_server():
    token_from_cache = True
    if (cache["token_exp"] - datetime.datetime.now()).total_seconds() < 600:
        url = 'https://api1.pal-es.com/v1/user/login'
        headers = {'Content-Type': 'application/json'}
        payload = {"username": USERNAME, "password": PASSWORD}
        r = requests.post(url, headers=headers, data=json.dumps(payload))
        token = json.loads(r.text)["user"]["token"]
        exp = json.loads(base64.urlsafe_b64decode(token.split('.')[1]+'==').decode("utf-8"))['exp']
        cache["token_exp"] = datetime.datetime.fromtimestamp(int(exp)//1000)
        cache["token"] = token
        token_from_cache = False
    
    token = cache["token"]
    url = 'https://api1.pal-es.com/v1/place/6aab1ef5-42d5-4cb8-8b6f-6ef16f3803ff/users?skip=0&limit=10&filter=&guest=true%27'
    headers = {"x-access-token": token}
    r = requests.get(url, headers=headers)
    cars = json.loads(r.text)["users"]["carsPresent"]
    return cars, token_from_cache

def lambda_handler(event, context):
    # TODO implement
    debug = False
    form_cache = False
    token_from_cache = False
    
    if cache["valid"] and (datetime.datetime.now() - cache["last_update"]).total_seconds() < 5:
        cars = cache["cars"]
        form_cache = True
    else:
        if debug:
            cars = 33
        else:
            cars, token_from_cache = get_cars_from_server()
        cache["valid"] = True
        cache["last_update"] = datetime.datetime.now()
        cache["cars"] = cars
    
    
    total = 70
    pregnant = 1
    handicap = 1
    
    freeSpace = total -  pregnant - handicap - cars
    
    res = {"available_spaces": freeSpace, "from_cache": form_cache, "token_from_cache": token_from_cache}
    
    return {
        'statusCode': 200,
        'headers': {"Access-Control-Allow-Origin": "*"},
        'body': json.dumps(res)
    }
