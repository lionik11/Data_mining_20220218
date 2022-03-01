from bs4 import BeautifulSoup
import requests
# import json
from pprint import pprint
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError


def search_vacancies_with_salary():
    salary_input = int(input("Введите желаемый уровень зарплаты:\n"))
    count_salary_vacancies = 0
    for doc in db.vacancies.find({'$or': [{'salary_min': {'$gte': salary_input}}, {'salary_max': {'$gte': salary_input}}]}):
        count_salary_vacancies += 1
        pprint(doc)
    print(f'Найдено {count_salary_vacancies} вакансий с желаемым уровнем зарплаты.')


def insert_vacancy_to_db(database, my_dict):
    global inserted_count
    try:
        result = database.find_one(my_dict)
        if not result:
            inserted_count += 1
            database.insert_one(my_dict)
    except DuplicateKeyError:
        print("Document is already exist")


# поиск информации о работодателе
def find_employer(my_vacancy):
    employer = my_vacancy.find('a', {'data-qa': "vacancy-serp__vacancy-employer"})
    if employer is not None:
        return employer.getText()
    else:
        return None


# поиск информации о местоположении вакансии
def find_address(my_vacancy):
    address = my_vacancy.find('div', {'data-qa': "vacancy-serp__vacancy-address"})
    if address is not None:
        return address.getText()
    else:
        return None


# поиск информации о зарплате вакансии
def find_salary(my_vacancy):
    salary = my_vacancy.find("span", {'data-qa': 'vacancy-serp__vacancy-compensation'})
    if salary is not None:
        salary_text = salary.getText()
        if salary_text.find("от") != -1:
            salary_min = int(''.join([i for i in salary_text if i.isdigit()]))
            salary_max = None
            return [salary_min, salary_max]
        elif salary_text.find("до") != -1:
            salary_min = None
            salary_max = int(''.join([i for i in salary_text if i.isdigit()]))
            return [salary_min, salary_max]
        else:
            salary_min = int(''.join([i for i in salary_text.split(' ')[0] if i.isdigit()]))
            salary_max = int(''.join([i for i in salary_text.split(' ')[2] if i.isdigit()]))
            return [salary_min, salary_max]
    else:
        salary_min = None
        salary_max = None
        return [salary_min, salary_max]


# функция скраппинга
def scrapping_data():
    global job_name
    for vacancy in vacancies:
        vacancy_data = {}
        info = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-title'})
        link = info['href']
        name = info.getText()
        salary_data = find_salary(vacancy)
        employer_text = find_employer(vacancy)
        address_text = find_address(vacancy)
        vacancy_data['name'] = name
        vacancy_data['link'] = link[:link.find('?')]
        vacancy_data['salary_min'] = salary_data[0]
        vacancy_data['salary_max'] = salary_data[1]
        vacancy_data['employer_text'] = employer_text
        vacancy_data['address_text'] = address_text
        vacancy_data['source'] = 'HeadHunter'
        vacancy_data['search_text'] = job_name
        insert_vacancy_to_db(db_vacancies, vacancy_data)


client = MongoClient('localhost', 27017)
db = client['user_LeoK']
db_vacancies = db.vacancies


base_url = 'https://hh.ru/'
headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/98.0.4758.102 Safari/537.36'}

# Ввод данных
job_name = input("Введите название вакансии:\n")
page_count = input("Введите количество страниц, которые Вы хотите выгрузить (в одной странице 20 вакансий). Если Вы хотите выгрузить все страницы, то введите любую бвукву.\n")

# Счетчики
page = 0
inserted_count = 0
k = True

if page_count.isdigit():
    page_count = int(page_count)
    while page < page_count:
        url = f"{base_url}search/vacancy?text={job_name}&salary=&currency_code=RUR&experience=doesNotMatter&order_by=relevance&search_period=0&items_on_page=20&no_magic=true&L_save_area=true&page={page}&hhtmFrom=vacancy_search_list"
        response = requests.get(url, headers=headers)
        dom = BeautifulSoup(response.text, 'html.parser')
        temp = dom.find('div', {"class": 'vacancy-serp'})
        vacancies = temp.find_all('div', {'class': "vacancy-serp-item"})
        scrapping_data()
        page += 1
    print(f"Добавлено {inserted_count} вакансий")
else:
    while k is not None:
        url = f"{base_url}search/vacancy?text={job_name}&salary=&currency_code=RUR&experience=doesNotMatter&order_by=relevance&search_period=0&items_on_page=20&no_magic=true&L_save_area=true&page={page}&hhtmFrom=vacancy_search_list"
        response = requests.get(url, headers=headers)
        dom = BeautifulSoup(response.text, 'html.parser')
        vacancies = dom.find_all('div', {'class': "vacancy-serp-item"})
        scrapping_data()
        page += 1
        k = dom.find('a', {'data-qa': "pager-next"})
    print(f"Добавлено {inserted_count} вакансий")

search_vacancies_with_salary()

# for doc in db.vacancies.find({}):
#     print(doc)
