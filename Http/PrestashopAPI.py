import subprocess, requests
from lxml import etree
import sys
from datetime import date

sys.path.insert(0, '../Tawssil')

from __auth__ import *
from Core.Formatter import Formatter
from utils import BASE_DIR


class PrestashopAPI:
    """
    Connection to PS Stores
    """
    @classmethod
    def getResponse(cls, url:str, apiKey:str):
        """
        Sometimes PS api fails so we try infinitely until success
        if it 
        """
        while 1:
            try:
                response = requests.get(url, auth=(apiKey, ''))
                return response
            except Exception as e:
                print(e)

    @classmethod
    def getStorePhone(cls, store, default="0661549874"):
        storePhones = {
            "Parapharma" : "0632478888",
            "Coinpara": "0694900900",
            "Parabio": "0694900900",
            "Allopara": "0631800800",
            "Maroc Event": "0665804951"
        }
        
        return storePhones.get(store, default)


    @classmethod
    def updateOrderStatus(cls, storeName:str, order_id:int) -> None:
        '''
        Change order status to "shipped (expedie/ encours de livraison)" using php script which connects to store via prestashop API \n
        See ../PHP/updateOrderStatus.php __DO NOT EDIT__ 
        '''
        if storeName.lower() == "parabio": storeName = "www.parabio"
        
        command = f'php "{BASE_DIR}\\PHP\\updateOrderStatus.php" {storeName} {order_id} {apiKey}'

        try:
            proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
            script_response = proc.stdout.read()

            return script_response.decode("utf-8")  
         
        except Exception as exception:
            return exception    


    @classmethod
    def orderData(cls, store, order_id):
        if store == "Parabio":
            storeName = 'www.parabio'
        else:
            storeName = store

        order_url = f'https://{storeName}.ma/api/orders/{order_id}'

        try:
            order_response = cls.getResponse(order_url, apiKey)
            order_root = etree.fromstring(order_response.content)
            createdDate = order_root.xpath('//invoice_date')[0].text[:10]
            total = int(order_root.xpath('//total_paid')[0].text[:-7])
            payment_type = order_root.xpath('//payment')[0].text
            if payment_type == 'cmi': total = 0

            # Address & Name
            address_id = order_root.xpath("//id_address_delivery")[0].text
            address_url = f'https://{storeName}.ma/api/addresses/{address_id}'
            address_response = cls.getResponse(address_url, apiKey)

            address_root = etree.fromstring(address_response.content)
            client_name = f'{address_root.xpath("//firstname")[0].text} {address_root.xpath("//lastname")[0].text}'

            try:
                address1 = address_root.xpath("//address1")[0].text
                address2 = address_root.xpath("//address2")[0].text
                if (address2) and (address1 != address2): address = f'{address1} {address2}'
                else: address = address1
            except:
                address = address_root.xpath("//address1")[0].text

            # City
            try: city = address_root.xpath("//city")[0].text.lower()
            except: city = ''
            
            country_url = f'https://{storeName}.ma/api/countries/{address_root.xpath("//id_country")[0].text}'
            country_response = cls.getResponse(country_url, apiKey)
                
            country_root = etree.fromstring(country_response.content)
            country = country_root.xpath('//name/language')[0].text.lower()
            
            client_city = Formatter.city(country) if Formatter.city(country) else Formatter.city(city)

            # Phone
            try:
                phone_mobile = address_root.xpath("//phone_mobile")[0].text
                phone_mobile = Formatter.phone(phone_mobile)
            except: phone_mobile = ''
            
            try:
                phone = address_root.xpath("//phone")[0].text
                phone = Formatter.phone(phone)
            except: phone = ''
            
            if (phone and phone_mobile) and (phone != phone_mobile):
                if phone_mobile.startswith('05') and phone:
                    phone_mobile, phone = phone, phone_mobile

        except Exception as e:
            return f'had commande makinach f {store} wla chi moshkil f site wla conx\n\nError :\n{e}\nerror line: {sys.exc_info()[-1].tb_lineno}'
            
        return {
            "id": order_id,
            "store": store,
            "created": createdDate,
            "shipped": f"{date.today()}",
            "delivered": "",
            "period": "",
            "delay": "",
            "name": client_name,
            "address" : address,
            "city" : client_city,
            "phone1" : phone_mobile if phone_mobile else phone,
            "phone2" : phone if phone else phone_mobile,
            "total": total,
            "status": "SHIPPED",
            "last_status": "",
            "deliveryCompany": "Tawssil",
        }
