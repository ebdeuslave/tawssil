import requests
import json
from bs4 import BeautifulSoup


class Tawssil:
    def __init__(self, username, password) -> None:
        self.username = username
        self.password = password
        
        
    @property
    def session(self) -> requests.Session:
        sess = requests.Session()
        front = sess.get("https://portail.tawssil.ma/web")
        soup = BeautifulSoup(front.text, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})['value'] 
        
        payload = {
            "csrf_token": csrf_token,
            "login": self.username,
            "password": self.password,
        }

        sess.post("https://portail.tawssil.ma/web/login", data=payload, cookies=sess.cookies)

        return sess
               
               
    def getPackages(self, limit=80):
        if limit > 80:
            raise Exception("Limit should not be > 80")
        
        OFFSET = 0 # must be fixed to 0 to begin from the 1st page
        packages = {
            "total": 0,
            "list": []
        }
        
        for _ in range(0, 1000):
            json_data = {
                'jsonrpc': '2.0',
                'method': 'call',
                'params': {
                    'model': 'cp.coli',
                    'domain': [],
                    'fields': [
                        'name',
                        'barcode',
                        'partner_barcode',
                        'ref_colis',
                        'create_date',
                        'partner_id',
                        'child_name',
                        'ship_from_city',
                        'ship_to_city',
                        'shipment_type',
                        'currency_id',
                        'is_return',
                        'partner_type',
                        'fees',
                        'cod',
                        'is_crbt_client_paid',
                        'state',
                        'statut',
                        'return_reason',
                    ],
                    'offset': OFFSET, # offset means "start from x+1 to limit, Ex: if offset=0 and limit=80 result will be from 1-80, offset=80 result: 81-160...etc"
                    'limit': limit, # max limit = 80
                    'sort': '',
                    'context': {
                        'lang': 'fr_FR',
                        'tz': 'Africa/Casablanca',
                        'uid': 49117,
                        'allowed_company_ids': [
                            1,
                        ],
                        'bin_size': True,
                    },
                },
            }
            
            response = requests.post('https://portail.tawssil.ma/web/dataset/search_read', cookies=self.session.cookies, json=json_data)
            
            try:
                if not response.json()["result"]["length"]:
                    # if length is 0 means the last page was the previous
                    return packages
                
                packages["total"] += response.json()["result"]["length"]
                packages["list"].extend(response.json()["result"]["records"])
              
            except:
                print(response.content)
                return
        
            OFFSET += limit # add limit X to offset to move to the next page
            
        return packages
            
            
    def savePackages(self, packages:list, filename="tawssil_packages.json"):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(packages["list"], f, ensure_ascii=False, indent=4)
        

tawssil = Tawssil("username", "password")

packages = tawssil.getPackages()

print("Total Packages:", packages["total"])

tawssil.savePackages(packages)

