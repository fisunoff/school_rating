import requests
import sqlite3
import json
import pprint
from qiwi_key import mylogin, api_access_token


class Payments:
    def __init__(self, TableName):
        self.tablename = TableName
        with sqlite3.connect("../db/payments.db") as connection:
            cursor = connection.cursor()
            cursor.execute(
                f"""CREATE TABLE IF NOT EXISTS {TableName} (transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                 user_id INTEGER, phone TEXT, sum INTEGER, success BOOL)""")
            connection.commit()

    def AddRecord(self, transaction_id, user_id, phone, summa, success):
        with sqlite3.connect("../db/payments.db") as connection:
            cursor = connection.cursor()
            cursor.execute(f"INSERT INTO {self.tablename} VALUES(?, ?, ?, ?, ?)",
                           (transaction_id, user_id, phone, summa, success))
            connection.commit()

    def GetRecord(self, transaction_id):
        with sqlite3.connect("../db/payments.db") as connection:
            cursor = connection.cursor()
            return cursor.execute(f"""SELECT * FROM {self.tablename} WHERE transaction_id = ?""",
                                  (transaction_id,)).fetchone()

    def ChangeRecord(self, transaction_id):
        with sqlite3.connect("../db/payments.db") as connection:
            cursor = connection.cursor()
            return cursor.execute(f"""UPDATE {self.tablename} SET success = ? WHERE transaction_id = ?""",
                                  (True, transaction_id))

    def payment_history_last(self, my_login=mylogin, api_access_token=api_access_token, rows_num="10",
                             operation_type="IN", next_TxnId="", next_TxnDate=""):
        s = requests.Session()
        s.headers['authorization'] = 'Bearer ' + api_access_token
        parameters = {'rows': rows_num, "operation": operation_type, 'nextTxnId': next_TxnId,
                      'nextTxnDate': next_TxnDate}
        h = s.get('https://edge.qiwi.com/payment-history/v2/persons/' + my_login + '/payments', params=parameters)
        return h.json()


Payments = Payments("Incoming")
data = Payments.payment_history_last()
result = Payments.GetRecord(1)

for i in range(len(data['data'])):
    if data['data'][i]['personId'] == int(result[2]):
        if data['data'][i]['comment'] == int(result[0]):
            if data['data'][i]['sum']['amount'] == int(result[3]):
                if data['data'][i]["status"] == "SUCCESS":
                    Payments.ChangeRecord(0)