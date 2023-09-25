(function () {
    var timestamp = getTime();
    pm.environment.set("timestamp",timestamp);

    const clientId = pm.environment.get("client_id");
    const secret = pm.environment.get("secret");

    var accessToken = "";
    if(pm.environment.has("easy_access_token")){
        accessToken = pm.environment.get("easy_access_token")
    }

    const httpMethod = pm.request.method.toUpperCase();
    const query = pm.request.url.query;
    const mode = pm.request.body.mode;
    const headers = pm.request.headers;
    
    // sha256
    var signMap = stringToSign(query, mode, httpMethod, secret)
    var urlStr = signMap["url"]
    var signStr = signMap["signUrl"]
    pm.request.url = pm.request.url.host + urlStr
    var nonce = ""
    if (headers.has("nonce")) {
        var jsonHeaders = JSON.parse(JSON.stringify(headers))
        jsonHeaders.forEach(function(item){
            if (item.key == "nonce" && !item.disabled) {
                nonce = headers.get("nonce")
            }
        })
    }
    var sign = calcSign(clientId, accessToken, timestamp, nonce, signStr, secret);
    pm.environment.set('easy_sign', sign);
})();

function getTime(){
    var timestamp = new Date().getTime();
    return timestamp;
}

// // Token verification calculation
// function calcSign(clientId,timestamp,nonce,signStr,secret){
//     var str = clientId + accessToken +timestamp + nonce + signStr;
//     var hash = CryptoJS.HmacSHA256(str, secret);
//     var hashInBase64 = hash.toString();
//     var signUp = hashInBase64.toUpperCase();
//     return signUp;
// }

// Business verification calculation
function calcSign(clientId,accessToken,timestamp,nonce,signStr,secret){
    var str = clientId + accessToken +timestamp + nonce + signStr;
    var hash = CryptoJS.HmacSHA256(str, secret);
    var hashInBase64 = hash.toString();
    var signUp = hashInBase64.toUpperCase();
    return signUp;
}

// Generate signature string
function stringToSign(query, mode, method, secret){
    var sha256 = "";
    var url = "";
    var headersStr = ""
    const headers = pm.request.headers;
    var map = {}
    var arr = []
    var bodyStr = ""
    if(query){
        toJsonObj(query, arr, map)
    }
    if (pm.request.body && mode) {
        if (mode != "formdata" && mode != "urlencoded"){
            bodyStr = replacePostmanParams(pm.request.body.toString())
        } else if (mode == "formdata") {
           // Traversing form key value pairs
            toJsonObj(pm.request.body["formdata"], arr, map)
        } else if (mode == "urlencoded") {
           // Traversing form key value pairs
            toJsonObj(pm.request.body["urlencoded"], arr, map)
        }
    } 
    sha256 = CryptoJS.SHA256(bodyStr)
    arr = arr.sort()
    arr.forEach(function(item){
            url += item + "=" + map[item] + "&"
    })
    if (url.length > 0 ) {
        url = url.substring(0, url.length-1)
        url = "/" + pm.request.url.path.join("/") + "?" + url
    } else {
        url = "/" + pm.request.url.path.join("/") 
    }
    
    if (headers.has("Signature-Headers") && headers.get("Signature-Headers")) {
        var jsonHeaders = JSON.parse(JSON.stringify(headers))
        var signHeaderStr = headers.get("Signature-Headers")
        const signHeaderKeys = signHeaderStr.split(":")
        signHeaderKeys.forEach(function(item){
            var val = ""
            if (isSelected(jsonHeaders,item) && headers.get(item)) {
                val = headers.get(item)
            }
            headersStr += item + ":" + val + "\n"
        })
    }
    var map = {}

    url = replacePostmanUrl(url)    
    map["signUrl"] = method + "\n" + sha256 + "\n" + headersStr + "\n" + url
    map["url"] = url
    return map
}

function isSelected(jsonHeaders,key){
    var result = true;
    jsonHeaders.forEach(function(item){
        if (item.key == key && item.disabled) {
            result = false
        }
    })
    return result
}

function replacePostmanParams(str){
    while(str.indexOf("{{")!=-1&&str.indexOf("}}")!=-1){
        const key = str.substring(str.indexOf("{{")+2,str.indexOf("}}"))
        var value = pm.environment.get(key)
        if(!value) value=""
        str = str.replace("{{"+key+"}}", value)
    }
    return str
}

function replacePostmanUrl(str){
    console.log("str:",str)
    while(str.indexOf("{{")!=-1&&str.indexOf("}}")!=-1){
        const key = str.substring(str.indexOf("{{")+2,str.indexOf("}}"))
        var value = pm.environment.get(key)
        if(!value) value=""
        str = str.replace("{{"+key+"}}", value)
    }

    while(str.indexOf(":")!=-1){
        const tempStr = str.substring(str.indexOf(":")+1,str.length);
        var key = "";
        if(tempStr.indexOf("/")!=-1){
            key = tempStr.substring(0,tempStr.indexOf("/"))
        }else if(tempStr.indexOf("?")!=-1){
            key = tempStr.substring(0,tempStr.indexOf("?"))
        }else {
            key = tempStr.substring(0,tempStr.length)
        }
        var value = pm.request.url.variables.get(key)
        if(!value) value=""
        str = str.replace(":"+key, value)
    }
    return str
}


function toJsonObj(params, arr, map){
    var jsonBodyStr = JSON.stringify(params)
    var jsonBody = JSON.parse(jsonBodyStr)
    jsonBody.forEach(function(item){
        if(!item.disabled){
            arr.push(item.key)
            map[item.key] = item.value
        }
    })
}