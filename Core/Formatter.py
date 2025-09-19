import re

class Formatter:

    @classmethod
    def phone(cls, phone_number):
        phone_number = re.sub('[^0-9]', '', phone_number)

        if phone_number.startswith('2120') : phone_number = phone_number[3:]
        elif phone_number.startswith('212') : phone_number = '0' + phone_number[3:]
        elif phone_number.startswith('002120') : phone_number = phone_number[5:]
        elif phone_number.startswith('00212') : phone_number = '0' + phone_number[5:]
        elif phone_number.startswith('0212') : phone_number = '0' + phone_number[4:]
        elif len(phone_number) == 9 and not phone_number.startswith('0'): phone_number = '0' + phone_number	

        if not phone_number.startswith("0") or len(phone_number) != 10:
            return False
        
        return phone_number
        
    @classmethod
    def city(cls, name):
        if not name or 'autre' in name or name == 'r.s.t':
            return ''

        name = name.replace('é', 'e').replace('è', 'e').replace('ê', 'e').replace('ë', 'e').replace('à', 'a').replace('á', 'a').replace('ä', 'a').replace("-", "").replace("ï", "i").strip()

        # Correct city name depends on Tawssil system - OUR SYSTEM VALUE: Tawssil VALUE
        CITIES = {}
            
        return CITIES.get(name, name)
    
    @classmethod
    def changed_fields(cls, order_data:dict, fields:dict):
        """
        Check if some fields changed manually
        """
        if fields["city"]: order_data["city"] = fields["city"]
        if fields["address"]: order_data["address"] = fields["address"]
        if type(fields["total"]) == int: order_data["total"] = fields["total"]
        if fields["phone"]: order_data["phone1"] = order_data["phone2"] = fields["phone"] 
        if fields["remark"]: order_data["remark"] = fields["remark"]
        