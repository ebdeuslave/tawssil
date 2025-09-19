import win32print
from Core.HandleJsonFiles import HandleJsonFiles

class Settings:
    @classmethod
    def apply(cls, settings:dict) -> None:
        HandleJsonFiles.edit(settings, "settings")
        cls.setDefaultPrinter(settings["printer"])
        
    @staticmethod
    def setDefaultPrinter(printerName:str) -> None:
        """
        win32print.EnumPrinters(2) returns nested tuples every tuple has 3 elements, the 3th one contains printer name
        """
        printers = win32print.EnumPrinters(2)
        
        available_printers = {
            "HP": printers[0][2], # HP LaserJet P2055dn (Index 4 = tuple contains printer info , index 2 = printer name)
            "Deli": printers[1][2] # Deli 740C Printer (Thermic)
        }
        
        win32print.SetDefaultPrinter(available_printers[printerName])
        
    @classmethod
    def getPrinter(cls) -> str:
        """
        Get the current default printer name from settings
        """
        return HandleJsonFiles.read("settings")["printer"]
    
    @classmethod
    def autoPrint(cls) -> bool:
        """
        Get auto print setting
        """
        return HandleJsonFiles.read("settings")["autoPrint"]["active"]
        
    @classmethod
    def totalToPrintAuto(cls) -> int:
        """
        Get total to print setting
        """
        return int(HandleJsonFiles.read("settings")["autoPrint"]["total_to_print"])
    