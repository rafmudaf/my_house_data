
import copy
import datetime;
import hashlib
import hmac
import json
import os
import requests


def get_timestamp():
    """
    Returns a timestamp in milliseconds in UTC.

    Returns:
        int: timestamp
    """
    timestamp = int(datetime.datetime.now().timestamp() * 1e3)
    return timestamp


def stringToSign(query, mode, method, secret, url):
    # Generate signature string
    headersStr = ""
    map = {}
    bodyStr = b""
    sha256 = hashlib.sha256(bodyStr).hexdigest()
    map = {}
    map["signUrl"] = method + "\n" + sha256 + "\n" + headersStr + "\n" + url
    map["url"] = url
    return map


def HmacSHA256(string, secret):
    return hmac.new(
        bytes(secret, 'latin-1'), 
        msg=bytes(string, 'latin-1'), 
        digestmod=hashlib.sha256
    ).hexdigest().upper()


def calcSignToken(clientId, timestamp, nonce, signStr, secret):
    # Token verification calculation
    string = clientId + str(timestamp) + nonce + signStr
    hash = HmacSHA256(string, secret)
    hashInBase64 = hash #.toString()
    signUp = hashInBase64 #.toUpperCase()
    return signUp


def get_auth(client_id, secret, url, timestamp):
    httpMethod = "GET"
    query = None
    mode = "raw"
    
    # sha256
    signMap = stringToSign(query, mode, httpMethod, secret, url)
    # urlStr = signMap["url"]
    signStr = signMap["signUrl"]
    # print(signStr)
    nonce = ""
    sign = calcSignToken(client_id, timestamp, nonce, signStr, secret)
    # pm.environment.set('easy_sign', sign);
    return sign


def calcSignBusiness(clientId, accessToken, timestamp, nonce, signStr, secret):
    # Business verification calculation
    string = clientId + accessToken + str(timestamp) + nonce + signStr
    hash = HmacSHA256(string, secret)
    hashInBase64 = hash #.toString()
    signUp = hashInBase64 #.toUpperCase()
    return signUp


def get_auth_business(client_id, accessToken, secret, url, timestamp):
    httpMethod = "GET"
    query = None
    mode = "raw"
    
    # sha256
    signMap = stringToSign(query, mode, httpMethod, secret, url)
    # urlStr = signMap["url"]
    signStr = signMap["signUrl"]
    # print(signStr)
    nonce = ""
    sign = calcSignBusiness(client_id, accessToken, timestamp, nonce, signStr, secret)
    # pm.environment.set('easy_sign', sign);
    return sign


if __name__ == "__main__":

    ### CONFIG
    if os.getenv('CI'):
        CLIENT_ID = os.getenv("CLIENT_ID")
        SECRET = os.getenv("SECRET")
    else:
        data = json.load(open("config.json", "r"))
        CLIENT_ID = data["CLIENT_ID"]
        SECRET = data["SECRET"]
    EASY_ACCESS_TOKEN = None
    HEADERS = {
        'client_id': CLIENT_ID,
        # 'access_token': '',
        # 'sign': '',
        # 't': '',
        'sign_method': 'HMAC-SHA256'
    }
    URL_HOST = "https://openapi.tuyaus.com/"

    device_ids = [
        "eb31c4a2913640b0d1xowo",  # Sensor 1 - hallway
        "ebf562fa0e3423e8cbmwfy",  # Sensor 2 - attic
        "eb17d322c22622aa27z5tl",  # Sensor 3 - bedroom
        "ebd316a0fbb97cc669d2pv",  # Sensor 4 - back room
        "eb26dc26a384eb3809rujs",  # Sensor 5 - kitchen
        "eb0594185e8a66f8b8f6cf",  # Sensor 6 - crawl space
    ]
    ###


    timestamp = get_timestamp()

    # Authenticate
    token_url = f"/v1.0/token?grant_type=1"

    headers = copy.deepcopy(HEADERS)
    headers["t"] = str(timestamp)
    headers["sign"] = get_auth(CLIENT_ID, SECRET, token_url, timestamp)
    response = requests.request(
        "GET",
        URL_HOST + token_url,
        headers=headers,
        data={}
    )
    response_data = response.json()
    t = response_data["t"]
    tid = response_data["tid"]
    success = response_data["success"]
    if not success:
        print(response.text)
        exit

    result = response_data["result"]
    access_token = result["access_token"]
    expire_time = result["expire_time"]
    refresh_token = result["refresh_token"]
    uid = result["uid"]

    print(response.json())

    temps, hums, batts = [], [], []
    headers["access_token"] = access_token
    for id in device_ids:
        device_URL = f"/v1.0/devices/{id}/status"
        headers["sign"] = get_auth_business(CLIENT_ID, access_token, SECRET, device_URL, timestamp)
        response = requests.request(
            "GET",
            URL_HOST + device_URL,
            headers=headers,
            data={}
        )
        response_data = response.json()
        t = response_data["t"]
        tid = response_data["tid"]
        success = response_data["success"]
        if not success:
            print(response.text)
            exit
            # TODO: fill with null data when the request fails

        result = response_data["result"] # Should be a list of data with form: [{"code":"va_temperature","value":260},{"code":"va_humidity","value":564},{"code":"battery_percentage","value":100}]
        for dp in result:
            match dp["code"]:
                case "va_temperature":
                    temps.append(dp["value"])
                case "va_humidity":
                    hum_dp = dp["value"]
                    if int(hum_dp) < 100:       # In some of the sensors, the humidity is reported without a digit for the decimal. Here, I assume the humidity will never be lower than 10%. If the value is less than 100 (10.0%), then assume it's two digits so shift the digits to the left.
                        hum_dp *= 10
                    hums.append(hum_dp)
                case "battery_percentage":
                    batts.append(dp["value"])

    with open("sensor_data.csv", "a") as datapointscsv:
        datastring = ",".join(
                [str(timestamp)] +
                [str(t) for t in temps] +
                [str(h) for h in hums] +
                [str(b) for b in batts]
            )
        datapointscsv.write("\n")
        datapointscsv.write(datastring)
