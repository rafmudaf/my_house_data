
import requests
import datetime;
import hashlib
import copy
import hmac


def getTime():
    timestamp = int(datetime.datetime.now().timestamp() * 1e6)
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
    CLIENT_ID = ''
    SECRET = ""
    EASY_ACCESS_TOKEN = None
    HEADERS = {
        'client_id': CLIENT_ID,
        'access_token': '',
        # 'sign': '',
        # 't': '',
        'sign_method': 'HMAC-SHA256'
    }
    URL_HOST = "https://openapi.tuyaus.com/"

    device_ids = {
    }
    ###


    timestamp = 1695657834092 # int(datetime.datetime.now().timestamp() * 1e6)
    # timestamp = int(datetime.datetime.now().timestamp() * 1e6)

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

    headers["access_token"] = access_token
    for name, id in device_ids.items():
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

        result = response_data["result"] # Should be a list of data with form: [{"code":"va_temperature","value":260},{"code":"va_humidity","value":564},{"code":"battery_percentage","value":100}]
        for dp in result:
            match dp["code"]:
                case "va_temperature":
                    current_temperature = dp["value"]
                case "va_humidity":
                    current_humidity = dp["value"]
                case "battery_percentage":
                    current_battery = dp["value"]

        print("temp:", current_temperature)
        print("humidity:", current_humidity)
        print("battery:", current_battery)