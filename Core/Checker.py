from .HandleJsonFiles import HandleJsonFiles

class Checker:
    @classmethod
    def order_added(cls, order_id):
        """
        Check if order has been added (b3d lmrat t9der tnsa w t add same order twice)
        """
        return order_id in HandleJsonFiles.read("history/addedOrders")
    
    @classmethod
    def order_shipped(cls, order_id):
        """
        Check if order was shipped before (t9der cmd mkhalsa online tkhrej 2 mrat)
        """
        shipped = [value["shipped"] for value in HandleJsonFiles.read("history/shipmentsHistory").values() if order_id == value["id"]]
        
        return shipped[0] if shipped else 0
    
    @classmethod
    def old_order(cls, store, order_id):
        """
        b3d lmrat t9der t scanner cmd dyl coinpara wtzreb wtkhali parapharma wl cmd kina f parapharma
        dnc l7al howa ntl3o notif ls cmds l9dam li 9el mn 190000 f id 
        """
        return (store == "Parapharma" and int(order_id) < 190000) or (store == "Coinpara" and int(order_id) < 18000)
    
    @classmethod
    def is_casablanca(cls, city):
        """
        Check if city = casablanca (kidiwha ls livreurs dyalna, wb3d lmrat client kidir casa bel ghalat)
        """
        return 'casablanca' in city
    
    
    @classmethod
    def total_returned(cls, phone):
        history = HandleJsonFiles.read("history/shipmentsHistory")
        returned = [value["phone1"] for value in history.values() if phone == value["phone1"] and value["status"] == "RETURNED"]
        
        return len(returned)