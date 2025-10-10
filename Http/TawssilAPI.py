import sys
import requests
sys.path.insert(0, "../Tawssil")
from __auth__ import *
from Http.PrestashopAPI import PrestashopAPI
from utils import generateJWT, generate_reference, getCityId


class TawssilAPI:
    """
    Docs : See Docs Dir
    IMPORTANT: 
        All methods should return dict("hasError": bool, "content": str)
    """
    
    api_urls = {
        "test": "https://dev.mobipreshipement.link/api/",
        "prod": "https://portail.tawssil.ma/api/"
    }
    
    token_data = generateJWT(SECRET_KEY, PARTNER_ID)
    
    if token_data["hasError"]:
        raise Exception(f'Error when generating JWT:\n{token_data["content"]}')
    
    headers = {'Content-Type': 'application/json', "Authorization": f"Bearer {token_data['content']}"} 

    endpoints = {
        "CreatePackage" : api_urls["prod"] + "create_colis",
        "UpdatePackage" : api_urls["prod"] + "update_colis",
        "GenerateLabel": api_urls["prod"] + "get_colis_label",
        "TrackPackage": api_urls["prod"] + "tracking_colis",
        }


    @classmethod
    def createPackage(cls, order_data:dict, type:str):
        try:
            ref = generate_reference()

            if type == "Normal":
                data = [
                    {
                        "picking_address": {
                            "name": order_data["store"],
                            "city": 19812, # Casablanca ID
                            "street": order_data["store"],
                            "street2": f"CMD N:{order_data['id']}" if order_data['id'] else " ",
                            "phone": PrestashopAPI.getStorePhone(order_data["store"])
                        },
                        "recipient_address": {
                            "city": getCityId(order_data["city"]),
                            "street": order_data["address"],
                            "street2": order_data["remark"],
                            "name": order_data["name"],
                            "phone": f'{order_data["phone1"]} | {order_data["phone2"]}' if order_data["phone1"] != order_data["phone2"] else order_data["phone1"],
                        },
                        "shipment_type": "home_delivery",  # home_delivery relay_point relay_point_drop_off
                        "cash_on_delivery": order_data["total"],
                        "parcel_reference": ref,
                        "barcode": ref,
                    }
                ]
                
            else:
                data = [
                    {
                        "picking_address": {
                            "city": getCityId(order_data["city"]),
                            "street": order_data["name"],
                            "street2": order_data["address"],
                            "name": order_data["name"],
                            "phone": f'{order_data["phone1"]} | {order_data["phone2"]}' if order_data["phone1"] != order_data["phone2"] else order_data["phone1"],
                        },
                        "recipient_address": {
                            "name": order_data["store"],
                            "city": 19812, # Casablanca ID
                            "street": "N95 Rue 90 Jamila 4 Sebata",
                            "street2": f"Retour Colis-CMD N:{order_data['id']}" if order_data['id'] else "Retour Colis",
                            "phone": "0661549874"
                        },
                        "shipment_type": "home_delivery",
                        "cash_on_delivery": 0,
                        "parcel_reference": ref,
                        "barcode": ref,
                    }
                ]
                
            package_data = {
                "partner_id": PARTNER_ID,
                "data": data
            }
            
            response = requests.post(url=cls.endpoints["CreatePackage"], json=package_data, headers=cls.headers)
            
            if response.json()["result"]["result"] == "NOK":
                return {"hasError": True, "content": response.json()["result"]["errors"]}
            
            elif response.json()["result"]["result"] == "OK":
                return {"hasError": False, "content": response.json()["result"]["data"][0]}
            
            else:
                return {"hasError": True, "content": response.json()}

        except Exception as exception:
            return {"hasError": True, "content": exception}
        
        
    @classmethod
    def generateLabel(cls, parcel_reference:str):
        """
        This method returns the pdf url
        """
        data = {
            "partner_id": PARTNER_ID,
            "parcel_references": [
                parcel_reference
            ]
        }
        
        try:
            response = requests.post(url=cls.endpoints["GenerateLabel"], json=data, headers=cls.headers)
            
            if response.json()["result"]["result"] == "NOK":
                return {"hasError": True, "content": response.json()["result"]["errors"]}
            
            elif response.json()["result"]["result"] == "OK":
                return {"hasError": False, "content": response.json()["result"]["label_url"][0]["label_url"]}
            
            else:
                return {"hasError": True, "content": response.json()}
            
        except Exception as exception:
            return {"hasError": True, "content": exception}


    @classmethod
    def updatePackage(cls, parcel_reference:str, newPackageData:dict):
        """
        Allowed fields: 
            {
                "recipient_phone": "",
                "recipient_street": "",
                "recipient_street2": "",
                "cash_on_delivery": 0
            }
        """
        packageData = {
            "partner_id": PARTNER_ID,
            "parcel_reference": parcel_reference,
            "data": newPackageData
        }
        
        try:
            response = requests.post(url=cls.endpoints["UpdatePackage"], json=packageData, headers=cls.headers)
            
            if response.json()["result"]["result"] == "NOK":
                return {"hasError": True, "content": response.json()["result"]["errors"]}
            
            elif response.json()["result"]["result"] == "OK":
                return {"hasError": False, "content": f"Package <{parcel_reference}> has updated"}
            
            else:
                return {"hasError": True, "content": response.json()}
            
        except Exception as exception:
            return {"hasError": True, "content": exception}
        
        
    @classmethod
    def trackPackage(cls, parcel_reference:str):
        packageData = {
              "partner_id": PARTNER_ID,
                "parcel_reference": parcel_reference
            }
        
        try:
            response = requests.post(url=cls.endpoints["TrackPackage"], json=packageData, headers=cls.headers)
            
            if response.json()["result"]["result"] == "NOK":
                return {"hasError": True, "content": response.json()["result"]["errors"]}
            
            elif response.json()["result"]["result"] == "OK":
                return {"hasError": False, "content": response.json()["result"]["data"]}
        
            else:
                return {"hasError": True, "content": response.json()}
            
        except Exception as exception:
            return {"hasError": True, "content": exception}
        