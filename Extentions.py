import requests
import json
from Config import API_KEY

class APIException(Exception):
    pass

class Converter:
    @staticmethod
    def get_price(quote: str, base: str, amount: str):
        if quote.upper() == base.upper():
            raise APIException(f"Невозможно перевести одинаковые валюты {base.upper()}.")

        try:
            quote in currency
        except KeyError:
            raise APIException(f"Не удалось обработать валюту {quote}")

        try:
            base in currency
        except KeyError:
            raise APIException(f"Не удалось обработать валюту {base}")

        try:
            amount = float(amount.replace(',', '.'))
        except ValueError:
            raise APIException(f"Не удалось обработь введенное количество - {amount}.")

        url = f"https://api.apilayer.com/exchangerates_data/convert?to={base.upper()}&from={quote.upper()}&amount={amount}"
        payload = {}
        headers = {"apikey": API_KEY}
        r = requests.get(url, headers=headers, data=payload)
        total_base = json.loads(r.content)['result']

        return round(total_base,3)

    def get_currency(self):
        url = f"https://api.apilayer.com/exchangerates_data/symbols"
        payload = {}
        headers = {"apikey": API_KEY}
        r = requests.get(url, headers=headers)
        curr = json.loads(r.content)['symbols']

        return curr

currency = Converter()
currency = currency.get_currency()