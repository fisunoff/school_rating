from data.qiwi_api import Payments
from data.qiwi_key import mylogin, api_access_token
import requests


def check_deposit(info):
    data = payment_history_last()
    for i in range(len(data['data'])):
        if data['data'][i]['personId'] == int(info["phone"]):
            if data['data'][i]['comment'].strip() == info["hash"].strip():
                if data['data'][i]['sum']['amount'] == int(info["sum"]):
                    if data['data'][i]["status"] == "SUCCESS":
                        return True
    return False


def payment_history_last(my_login=mylogin, api_access_token=api_access_token, rows_num="10",
                         operation_type="IN", next_TxnId="", next_TxnDate=""):
    s = requests.Session()
    s.headers['authorization'] = 'Bearer ' + api_access_token
    parameters = {'rows': rows_num, "operation": operation_type, 'nextTxnId': next_TxnId,
                  'nextTxnDate': next_TxnDate}
    h = s.get('https://edge.qiwi.com/payment-history/v2/persons/' + my_login + '/payments', params=parameters)
    return h.json()


Payments_object = Payments("Incoming")
data = {'user_id': 2, 'phone': '79176546462', 'sender_phone': '', 'sum': 1, 'hash': '6e9918afb02639bc', 'success': 0}
print(data)
print(check_deposit(data))
# print(payment_history_last()["data"][0])
