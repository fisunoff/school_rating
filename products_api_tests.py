from requests import get, post, delete
import datetime, json

# для успешного прохождения всех групп тестов нужно удалить продукт номер 4, если он существует
# для этого раскомментируйте строку ниже
# print(delete('http://localhost:5000/secret_api/products/Q0oaaSor5RfnWXrOYNNnx6QveWJ8A755qWeMfwR0/4').json())

# тесты получения продукта
print(get('http://localhost:5000/api/products').json())
# ok

print(get('http://localhost:5000/api/products/1').json())
# ok

print(get('http://localhost:5000/api/products/99').json())
# такого продукта нет в БД

print(get('http://localhost:5000/api/products/qwerty').json())
# неверный параметр


# тесты добавления нового продукта
print(post('http://localhost:5000/secret_api/products/abrakadabra',
           json={"id": 4, 'title': "test1", 'quantity': 13, 'price': 273, "description": "test product",
                 "category": "no category", "user_id": 6}).json())
# не сработает, несуществующий секретный ключ

print(post('http://localhost:5000/secret_api/products/Q0oaaSor5RfnWXrOYNNnx6QveWJ8A755qWeMfwR0',
           json={"id": 4, 'title': "test1", 'quantity': 13, 'price': 273, "description": "test product",
                 "category": "no category", "user_id": 6}).json())
# сработает, ошибок нет

print(post('http://localhost:5000/secret_api/products/Q0oaaSor5RfnWXrOYNNnx6QveWJ8A755qWeMfwR0',
           json={"id": 4, 'title': "test1", 'quantity': 13, 'price': 273, "description": "test product",
                 "category": "no category", "user_id": 6}).json())
# не сработает, продукт с таким id уже есть

print(post('http://localhost:5000/secret_api/products/Q0oaaSor5RfnWXrOYNNnx6QveWJ8A755qWeMfwR0',
           json={"id": 5, 'title': "test1", "description": "test product",
                 "category": "no category", "user_id": 4}).json())
# не сработает, не все аргументы указаны

print(post('http://localhost:5000/secret_api/products/Q0oaaSor5RfnWXrOYNNnx6QveWJ8A755qWeMfwR0').json())
# не сработает, т.к. ничего не передаем

print(get('http://localhost:5000/api/products').json())
# Проверка. Продукт добавился


# тесты удаления продукта
print(delete('http://localhost:5000/secret_api/products/abrakadabra/4').json())
# продукт не удалился, неверный секретный ключ

print(delete('http://localhost:5000/secret_api/products/Q0oaaSor5RfnWXrOYNNnx6QveWJ8A755qWeMfwR0/4').json())
# продукт удалился

print(delete('http://localhost:5000/secret_api/products/Q0oaaSor5RfnWXrOYNNnx6QveWJ8A755qWeMfwR0/4').json())
# получаем ошибку. Такого продукта уже нет

print(delete('http://localhost:5000/secret_api/products/Q0oaaSor5RfnWXrOYNNnx6QveWJ8A755qWeMfwR0/qwerty').json())
# получаем ошибку. Неверный формат

print(get('http://localhost:5000/api/products').json())
# # Проверка. Продукт номер 4 удалился
