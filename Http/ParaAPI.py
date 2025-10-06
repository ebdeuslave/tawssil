import requests

class ParaAPI:
    """
    Connection to Para web apps
    """

    @classmethod
    def add_payment(cls, data):
        """
        Add refunded amount to virement web app
        """
        url = 'http://cheques-virements.local:8003/api/virements/add_virement/'

        response = requests.post(url=url, json=data)

        return response

    @classmethod
    def add_refund(cls, data):
        """
        Add refund to refund web app
        """
        url = "http://remboursement.local:8006/api/add_refund"

        response = requests.post(url, json=data)

        return response