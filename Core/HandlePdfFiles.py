from PyPDF2 import PdfMerger
import os, win32api
from datetime import datetime
import requests


class HandlePdfFiles:

    @classmethod
    def merge(cls, pdf_dir):
        merger = PdfMerger()

        merged_file_name = f'Labels-{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.pdf'

        merged_file_abs_path = f"{pdf_dir}/{merged_file_name}"
    
        pdf_files = [f"{pdf_dir}/{pdf}" for pdf in os.listdir(pdf_dir) if pdf.endswith('pdf')]

        if not pdf_files: 
            return "No PDF Found"
        
        try:
            for pdf_file in pdf_files:
                merger.append(pdf_file, import_outline=False)
                    
            merger.write(merged_file_abs_path)
            merger.close()
                    
            return os.path.abspath(merged_file_abs_path)
        
        except Exception as exception:
            return str(exception)
     
   
    @classmethod
    def download(cls, pdf_url, pdf_file):
        response = requests.get(pdf_url)

        if response.headers["Content-Type"] != "binary/octet-stream":
            return {
            "hasError": True,
            "content": response.content
        }
            
        return {
            "hasError": False,
            "content": pdf_file.write_bytes(response.content)
        }
        
        
    @classmethod
    def print(cls, pdf_file):
        win32api.ShellExecute(0, "print", pdf_file, None,  ".",  0)
