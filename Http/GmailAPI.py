import sys, os
sys.path.insert(0, '../Tawssil')
from utils import getLastPaymentDatetime
import ezgmail


class GmailAPI:

    def __init__(self, tokenFile, credentialsFile):
        ezgmail.init(tokenFile = tokenFile, credentialsFile = credentialsFile)
        

    def downloadAttachement(self, data, downloadFolder):
        try:
            results = ezgmail.search(f'from:{data["sender"]}', maxResults=data["maxResult"]) 

            index = 1
            total = 0

            for result in results:  
                if result.latestTimestamp() > getLastPaymentDatetime():
                    try:
                        for message in result.messages:
                            for attachment in message.attachments:
                                message.downloadAttachment(attachment, downloadFolder=downloadFolder)
                            os.chdir(downloadFolder)
                            # os.rename(attachment, f"{index}-{attachment}")
                            # index += 1
                            total += 1

                    except Exception as exeption:
                        print(exeption)
                        continue

            if not total:
                return {"hasError": True, "content": "No new payments found"} 
            
            return {"hasError": False, "content": results[0].latestTimestamp()} 
                
         
        except Exception as exception:
            return {"hasError": True, "content": exception}  
