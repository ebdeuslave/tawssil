import os, shutil, json, random, sys, jwt
from datetime import datetime


BASE_DIR = os.getcwd()

def emptyDirectory(dir) -> None:
    """
    Empty Directory \n
    params : Directory name -> str \n
    return : None
    """
    os.chdir(BASE_DIR)
    if os.path.isdir(dir): shutil.rmtree(dir)
    os.makedirs(dir)


def getPeriodByDay(shippingDate, deliveryDate):
    shippingDate = datetime.strptime(shippingDate, "%Y-%m-%d")
    deliveryDate = datetime.strptime(deliveryDate, "%Y-%m-%d")

    period = deliveryDate - shippingDate

    return period.days


def getLastPaymentDatetime() -> datetime:
    """
    Get last payment datetime to check new ones
    """
    
    last_payment_datetime = json.load(open(f"{BASE_DIR}/logs/last_payment.json", "r"))["datetime"]

    return datetime.strptime(last_payment_datetime, "%Y-%m-%d %H:%M:%S")


def setLastPaymentDatetime(payment_datetime) -> None:
    # set latest payment datetime to avoid checking the old ones
    file_path = f"{BASE_DIR}/logs/last_payment.json"
    last_payment = json.load(open(file_path, "r"))
    last_payment["datetime"] = payment_datetime
    dump_json = json.dumps(last_payment, indent=4)

    with open(file_path, "w") as f:
        f.write(dump_json)
      
        
def addToLogs(data:dict):
    file_path = f"{BASE_DIR}/logs/payment_logs.txt"
    
    with open(file_path, "a") as file:
        file.write(json.dumps(data) + "\n\n")
    
    
def generate_reference() -> str:    
    from Core.HandleJsonFiles import HandleJsonFiles
    while 1:
        ref = ''.join(str(random.randint(0, 9)) for _ in range(10))
        
        if ref not in HandleJsonFiles.read("history/shipmentsHistory") and not ref.startswith("0"):
            return ref
        
    
def generateJWT(secret_key, partner_id):
    try:
        headers_jwt = {
        "alg": "HS256",
        "typ": "JWT",
        "partner_id": partner_id
        }

        token = jwt.encode({}, secret_key, algorithm="HS256", headers=headers_jwt)
        
        return {"hasError": False, "content": token}

    except Exception as exception:
        return {"hasError": True, "content": f"{exception},'\nerror line: ',{sys.exc_info()[-1].tb_lineno}"}

       
def getCityId(cityName):
    cities = json.load(open("json_files/tawssil/cities.json", "r"))
    
    return cities.get(cityName, -1)


def getTawssilCities():
    import requests

    cookies = {
        'messagesUtk': '492550a7ab6944359dc58afeddfd7966',
        'session_id': 'f7b7f83669bdc0411f7e381ef7291d732d93c6f1',
        'frontend_lang': 'fr_FR',
        'tz': 'Africa/Casablanca',
    }

    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7,ar;q=0.6',
        'content-type': 'application/json',
        'origin': 'https://portail.tawssil.ma',
        'priority': 'u=1, i',
        'referer': 'https://portail.tawssil.ma/web',
        'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    json_data = {
        'jsonrpc': '2.0',
        'method': 'call',
        'params': {
            'model': 'res.city',
            'domain': [],
            'fields': [
                'name',
                'zipcode',
                'country_id',
                'state_id',
                'hub_id',
            ],
            'limit': 80,
            'offset': 0,
            'sort': '',
            'context': {
                'lang': 'fr_FR',
                'tz': 'Africa/Casablanca',
                'uid': 49117,
                'allowed_company_ids': [
                    1,
                ],
                'params': {
                    'action': 571,
                    'cids': 1,
                    'menu_id': 264,
                    'model': 'res.city',
                    'view_type': 'list',
                },
                'create': 0,
                'bin_size': True,
            },
        },
        'id': 33820801,
    }

    cities = {}

    for _ in range(9):
        response = requests.post('https://portail.tawssil.ma/web/dataset/search_read', cookies=cookies, headers=headers, json=json_data)

        records = response.json()["result"]["records"]

        for record in records:
            id = record['id']
            name = record['name'].lower().replace("\u00a0", " ").replace("\u200b", "").replace("â€‹", "")
            if "zone non desservie" not in name:
                cities[name]= id
            
        json_data["params"]["offset"] += 80
    
    print(len(cities))
    with open("json_files/tawssil/new_cities.json", "w", encoding="utf-8") as f:
        json.dump(cities, f, indent=4, ensure_ascii=False)

    
def updateTodayOrdersStatus():
    from Core.HandleJsonFiles import HandleJsonFiles
    from Http.PrestashopAPI import PrestashopAPI
    from datetime import date

    ids = {order["id"]:order["store"] for order in HandleJsonFiles.read("history/shipmentsHistory").values() if order["shipped"] == str(date.today())}

    for id, store in ids.items():
        
        result = PrestashopAPI.updateOrderStatus(store, id)
        
        print(result)