import requests
import sqlite3
import json
import pprint
import random
from data.qiwi_key import mylogin, api_access_token


class Payments:
    def __init__(self, TableName):
        self.tablename = TableName
        with sqlite3.connect("db/payments.db") as connection:
            cursor = connection.cursor()
            cursor.execute(
                f"""CREATE TABLE IF NOT EXISTS {TableName} (transaction_id INTEGER PRIMARY KEY,
                 user_id INTEGER, phone TEXT, sender_phone TEXT,sum INTEGER, hash TEXT, success BOOL)""")
            connection.commit()

    # функция добавления новой записи в БД
    def AddRecord(self, user_id, phone, sender_phone, summa, hash, success):
        with sqlite3.connect("db/payments.db") as connection:
            cursor = connection.cursor()
            cursor.execute(
                f"INSERT INTO {self.tablename} (user_id, phone, sender_phone, sum, hash, success) VALUES(?, ?, ?, ?, ?, ?)",
                (user_id, phone, sender_phone, summa, hash, success))
            connection.commit()

    # функция получения записи из БД по хешу
    def GetRecord(self, hash):
        with sqlite3.connect("db/payments.db") as connection:
            cursor = connection.cursor()
            return cursor.execute(f"""SELECT * FROM {self.tablename} WHERE hash = ?""",
                                  (hash,)).fetchone()

    # функция изменения записи(нужна для добавления в БД номера клиента, с которого произошло успешное пополнение)
    def ChangeRecord(self, hash, sender_phone):
        with sqlite3.connect("db/payments.db") as connection:
            cursor = connection.cursor()
            return cursor.execute(f"""UPDATE {self.tablename} SET sender_phone = ?, success = ? WHERE hash = ?""",
                                  (sender_phone, True, hash))

    # функция для начала пополнения баланса
    def deposit_money_request(self, user_id, summa):
        hash = Payments.make_hash(self)
        self.AddRecord(user_id, mylogin, "", summa, hash, 0)
        return {"user_id": user_id, "phone": mylogin, "sender_phone": "", "sum": summa, "hash": hash, "success": 0}

    # функция проверки успешности пополнения. В случае успешного пополнения добавит в БД номера клиента,
    # с которого произошло успешное пополнение и вернет True(можно зачислять деньги на баланс на сайте)
    def check_deposit(self, info):
        data = Payments.payment_history_last(self)
        for i in range(len(data['data'])):
            if data['data'][i]['personId'] == int(info["phone"]):
                if data['data'][i]['comment'].strip() == info["hash"].strip():
                    if data['data'][i]['sum']['amount'] == int(info["sum"]):
                        if data['data'][i]["status"] == "SUCCESS":
                            self.ChangeRecord(info["hash"], data['data'][i]["account"].strip("+"))
                            return True
        return False

    # функция для работы с QIWI API (Получение последних транзакций)
    def payment_history_last(self, my_login=mylogin, api_access_token=api_access_token, rows_num="10",
                             operation_type="IN", next_TxnId="", next_TxnDate=""):
        s = requests.Session()
        s.headers['authorization'] = 'Bearer ' + api_access_token
        parameters = {'rows': rows_num, "operation": operation_type, 'nextTxnId': next_TxnId,
                      'nextTxnDate': next_TxnDate}
        h = s.get('https://edge.qiwi.com/payment-history/v2/persons/' + my_login + '/payments', params=parameters)
        return h.json()

    # функция для хеширования операции. Данное значение пользователь будет вводить в комментарий к платежу
    def make_hash(self):
        return "%016x" % random.getrandbits(64)


# Payments = Payments("Incoming")
# # Payments.AddRecord(1, "79176546462", "78005553535", 100, Payments.make_hash(), 0)
# # data = Payments.payment_history_last()
# # print(data)
# # result = Payments.GetRecord("6d702c37f15be272")
# # print(result)
#
#
# ## колхозная(отладочная конструкция) пополнения
# # info = Payments.deposit_money_request(3, 1) # вот тут хеш ae9f3704a2455684
# info = Payments.GetRecord("ae9f3704a2455684")
# print(info)
# # создаю словарь и отправляю его в функцию для проверки корректности пополнения
# info = {"user_id": 3, "phone": 79176546462, "sender_phone": "", "sum": 1, "hash": "ae9f3704a2455684", "success": 0}
# print(Payments.check_deposit(info))
#
# # нормальная(релизная конструкция) пополнения
# # print(Payments.check_deposit(Payments.deposit_money_request(USER_ID, SUMMA)))


