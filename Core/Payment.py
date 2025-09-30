import pandas as pd
from .HandleJsonFiles import HandleJsonFiles
from datetime import datetime
import sys, re
sys.path.append("../Tawssil")
from configuration import MAX_SHIPPING_FEE, TAX_FEE, TAWSSIL_ID
from Http.ParaAPI import ParaApi



class Payment:
    def __init__(self, data={}):
        self.data = data
        self.logs = {
            "hasError": False,
            "hasWarning": False,
            "content": {
                "ERROR": None,
                "TRANSFER_DATE": None,
                "TRANSFERED_AMOUNT": 0,
                "PAID": 0,
                "NOT_SAME_AMOUNT": [],
                "NOT_FOUND": [],
                "EXCEED_SHIPPING_FEES": [],
            }
        }
    
    def set(self, file:str) -> dict:
        """
        Change shipments status to PAID
        """
        try:
            df = pd.read_excel(file)
            
            print(df)
            
            return
                
            self.logs["content"]["TRANSFER_DATE"] = datetime.strptime(df["Transfer date"][0], "%d %B %Y").strftime("%Y-%m-%d")
                        
            history = HandleJsonFiles.read("history/shipmentsHistory")  
            
            packagesNumbers = [re.sub("[^0-9]", "", packageNumber) for packageNumber in df["Référence colis"]]
            
            collectedAmounts = [amount for amount in df["CRBT"] if type(amount) == int]
            
            shippingFees = [shippingFees * TAX_FEE for shippingFees in df["Frais"] if type(shippingFees) == float or type(shippingFees) == int]
            
            # remove total amounts if exists
            if len(packagesNumbers) < len(collectedAmounts):
                collectedAmounts.pop()
                shippingFees.pop()

            self.logs["content"]["TRANSFERED_AMOUNT"] = int( sum(collectedAmounts) - sum(shippingFees) )   
            
            packages = [
                {
                    "number": packageNumber,
                    "amount": amount,
                    "shippingFee": shippingFee
                } for packageNumber, amount, shippingFee in zip(packagesNumbers, collectedAmounts, shippingFees)
            ]
            
            packages = list(filter(lambda package: package["shippingFee"] != 0, packages))

            for package in packages:
                if package["number"] not in history:
                    self.logs["content"]["NOT_FOUND"].append(package["number"])
                else: 
                    original_amount = history[package["number"]]["total"]
                    if original_amount != package["amount"] and history[package["number"]]["status"] != "RETURNED":
                        history[package["number"]]["last_status"] = f"PAID:{package['amount']}"
                        self.logs["hasWarning"] = True
                        self.logs["content"]["NOT_SAME_AMOUNT"].append({"packageNumber":package["number"], "originalAmount" : original_amount, "transferAmount": package["amount"]})
                        
                    history[package["number"]]["status"] = "PAID"
                    self.logs["content"]["PAID"] += 1
                        
                    if package["shippingFee"] > MAX_SHIPPING_FEE:
                        self.logs["hasWarning"] = True
                        self.logs["content"]["EXCEED_SHIPPING_FEES"].append({"packageNumber":package["number"], "shippingFee" : package["shippingFee"]})
                        
                        
            self.data = {
                "societe": TAWSSIL_ID,
                "date": self.logs["content"]["TRANSFER_DATE"],
                "montant": self.logs["content"]["TRANSFERED_AMOUNT"]
            }
        
            HandleJsonFiles.edit(history, "history/shipmentsHistory")
            
        except Exception as exception:
            self.logs["hasError"] = True
            self.logs["content"]["ERROR"] = f"{exception},'\nerror line: ',{sys.exc_info()[-1].tb_lineno}"
            
        return self.logs
               
            
    def add(self):
        """
        Add refunded amount to virement web app
        """
        if not self.data:
            return {"hasError": True, "content": "data is empty"}
        
        response = ParaApi.add_payment(self.data)

        try:
            if not response.json()["created"]:
                return {"hasError": True, "content": response.json()['error']}
                
            return {"hasError": False, "content": "done"}
        
        except Exception as exception:
            return {
                "hasError": True,
                "content": f"{exception},'\nerror line: ',{sys.exc_info()[-1].tb_lineno}"
                }
                
            

        