import json
import requests

# вводные данные пользователя и адреса API
username = "lionik11"
url = f"https://api.github.com/users/{username}/repos"
headers = "Accept: application/vnd.github.v3+json"

# составление запроса
my_request = requests.get(url, headers)
data = my_request.json()

# вывод на экран названий репозиториев пользователя
print(f"У пользователя {username} имеются репозитории:")
[print(f"{x['name']}") for x in data]

# запись в json-файл полной информации о репозиториях
json_filename = f"{username}_repositories.json"
with open(json_filename, 'w') as outfile:
    json.dump(data, outfile)
