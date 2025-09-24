import requests
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
               
               
    def getPackages(self, total_pages=100):
        packages = {
            "total": 0,
            "list": []
        }
        for offset in range(80, total_pages):
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
                    'offset': offset,
                    'limit': 80,
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
                packages["total"] += response.json()["result"]["length"]
                packages["list"].extend(response.json()["result"]["records"])
                return {
                    "total": response.json()["result"]["length"],
                    "packages": response.json()["result"]["records"]
                }
            except:
                print(response.content)
        
            offset += 80
            
username = "PARApharma"
password = "20Parapharmacie@Leader24"

tawssil = Tawssil(username, password)

packages = tawssil.getPackages()

print(packages)