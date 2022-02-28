from bs4 import BeautifulSoup
import requests
import json
from pprint import pprint


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
def scrapping_data(my_vacancies_list):
    global v_id
    for vacancy in vacancies:
        vacancy_data = {}
        info = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-title'})
        link = info['href']
        name = info.getText()
        salary_data = find_salary(vacancy)
        employer_text = find_employer(vacancy)
        address_text = find_address(vacancy)

        vacancy_data['v_id'] = v_id
        vacancy_data['name'] = name
        vacancy_data['link'] = link
        vacancy_data['salary_min'] = salary_data[0]
        vacancy_data['salary_max'] = salary_data[1]
        vacancy_data['employer_text'] = employer_text
        vacancy_data['address_text'] = address_text
        vacancy_data['source'] = 'HeadHunter'
        my_vacancies_list.append(vacancy_data)
        v_id += 1
    return my_vacancies_list


base_url = 'https://hh.ru/'
headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/98.0.4758.102 Safari/537.36'}

# Ввод данных
job_name = input("Введите название вакансии:\n")
page_count = input("Введите количество страниц, которые Вы хотите выгрузить (в одной странице 20 вакансий). Если Вы хотите выгрузить все страницы, то введите любую бвукву.\n")
vacancies_list = []

# Счетчики
page = 0
v_id = 1
k = True

if page_count.isdigit():
    page_count = int(page_count)
    while page < page_count:
        url = f"{base_url}search/vacancy?text={job_name}&salary=&currency_code=RUR&experience=doesNotMatter&order_by=relevance&search_period=0&items_on_page=20&no_magic=true&L_save_area=true&page={page}&hhtmFrom=vacancy_search_list"
        # url = f"{base_url}search/vacancy?area=113&search_field=name&search_field=company_name&items_on_page=20&search_field=description&text={job_name}&page={page}&hhtmFrom=vacancy_search_list%2F/"
        response = requests.get(url, headers=headers)
        dom = BeautifulSoup(response.text, 'html.parser')
        temp = dom.find('div', {"class": 'vacancy-serp'})
        vacancies = temp.find_all('div', {'class': "vacancy-serp-item"})
        scrapping_data(vacancies_list)
        page += 1
else:
    while k is not None:
        url = f"{base_url}search/vacancy?text={job_name}&salary=&currency_code=RUR&experience=doesNotMatter&order_by=relevance&search_period=0&items_on_page=20&no_magic=true&L_save_area=true&page={page}&hhtmFrom=vacancy_search_list"
        # url = f"{base_url}search/vacancy?area=113&search_field=name&search_field=company_name&items_on_page=20&search_field=description&text={job_name}&page={page}&hhtmFrom=vacancy_search_list%2F/"
        response = requests.get(url, headers=headers)
        dom = BeautifulSoup(response.text, 'html.parser')
        vacancies = dom.find_all('div', {'class': "vacancy-serp-item"})
        scrapping_data(vacancies_list)
        page += 1
        k = dom.find('a', {'data-qa': "pager-next"})

pprint(vacancies_list)

with open("vacancies_list.json", 'w') as outfile:
    json.dump(vacancies_list, outfile)
