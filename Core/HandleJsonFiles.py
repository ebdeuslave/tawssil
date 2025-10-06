import json, os, sys
sys.path.insert(0, '../Tawssil')
from utils import BASE_DIR

class HandleJsonFiles:
    """
    CRUD Json Files
    """

    @classmethod
    def create(cls, filesNames=[]) -> None:
        """
        Create json files \n
        params : Json file names -> list of str \n
        return : None
        """
        if not os.path.isdir(f"{BASE_DIR}/json_files"): os.makedirs(f"{BASE_DIR}/json_files")
        for fileName in filesNames:
            if not os.path.isfile(f'{BASE_DIR}/json_files/{fileName}.json'):
                with open(f'{BASE_DIR}/json_files/{fileName}.json', "x") as f:
                    f.write("{}")


    @classmethod
    def read(cls, json_file) -> dict: 
        """
        Read json file \n
        params : Json file name -> str \n
        return : Dict object
        """
        return json.load(open(f"{BASE_DIR}/json_files/{json_file}.json", "r"))


    @classmethod
    def add(cls, key, value, json_file) -> None:
        """
        Add to Json file \n
        params : key, value, file name -> strings \n
        return : None
        """
        content = cls.read(json_file)

        if key not in content:
            content[key] = value

            dump_json = json.dumps(content, indent=4)

            with open(f"{BASE_DIR}/json_files/{json_file}.json", "w") as f:
                f.write(dump_json)


    @classmethod
    def delete(cls, key, json_file) -> None:
        """
        Delete from Json file \n
        params : key -> str \n
        return : None
        """
        content = cls.read(json_file)

        if key in content:
            del content[key]

            dump_json = json.dumps(content, indent=4)

            with open(f"{BASE_DIR}/json_files/{json_file}.json", "w") as f:
                f.write(dump_json)


    @classmethod
    def edit(cls, content, json_file):
        dump_json = json.dumps(content, indent=4)

        with open(f"{BASE_DIR}/json_files/{json_file}.json", "w") as f:
            f.write(dump_json)


    @classmethod
    def empty(cls, file) -> None:
        """
        Empty Json file \n
        params : file name -> str \n
        return : None
        """
        if os.path.isfile(f"{BASE_DIR}/json_files/{file}.json"):
            with open(f"{BASE_DIR}/json_files/{file}.json", "w") as f:
                f.write("{}")

    @classmethod
    def saveToHistory(cls, shipmentNumber, order_data, order_id):
        if order_data["delivery_type"] != "Return":
            # save order for : status changing, detect if order doubled
            cls.add(order_id, order_data["store"], "history/addedOrders")
        # save shipment number for : generating label
        cls.add(f"Shipment{shipmentNumber}", shipmentNumber, "history/readyToPrint")
        # save data to history
        cls.add(shipmentNumber, order_data, "history/shipmentsHistory")
