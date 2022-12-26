import requests
import unicodedata
from bs4 import BeautifulSoup
from fake_headers import Headers
from pprint import pprint


def get_headers():
    return Headers().generate()


host = 'https://hh.ru/search/vacancy?text=python&area=1&area=2&order_by=publication_time'
hh_html = requests.get(url=host, headers=get_headers()).text
hh_soup = BeautifulSoup(hh_html, features='lxml')
article_hh = hh_soup.find(class_='vacancy-serp-content')
article_hh_tag = article_hh.find_all(class_='serp-item__title')
article_hh_tag_length = len(article_hh_tag)
vacancy_list = []

for i, tag in enumerate(article_hh_tag):
    symbol_bar = '█'
    step_bar = 100 / article_hh_tag_length
    print(end='\r')
    print(f'Загрузка вакансий {symbol_bar * (i + 1)} {round(step_bar * (i + 1), 2)} ', end='')

    article_link = tag['href']
    vacancy_html = requests.get(article_link, headers=get_headers()).text
    vacancy_soup = BeautifulSoup(vacancy_html, features='lxml')
    vacancy_body = vacancy_soup.find(class_='vacancy-description')
    if 'django' in str(vacancy_body).lower() and 'flask' in str(vacancy_body).lower():
        vacancy_title = vacancy_soup.find(attrs={'data-qa': 'vacancy-title'}).text
        company_name = vacancy_soup.find(attrs={'data-qa': 'bloko-header-2'}).text
        if (city_info := vacancy_soup.find(attrs={'data-qa': 'vacancy-view-raw-address'})) is not None:
            city_info = list(city_info)[0]
        else:
            city_info = vacancy_soup.find(attrs={'data-qa': 'vacancy-view-location'}).text
        salary = vacancy_soup.find(attrs={'data-qa': 'vacancy-salary'}).text
        if 'usd' in str(salary).lower():
            USD = True
        else:
            USD = False
        vacancy_list.append({
                                'Ссылка на вакансию': article_link,
                                'Название вакансии': vacancy_title,
                                'Название компании': unicodedata.normalize("NFKD", company_name),
                                'Город': city_info,
                                'Зарплата': unicodedata.normalize("NFKD", salary),
                                'USD': USD
                             })

print()
while(True):
    choice = str(input('Отобрать вакансии с ЗП только в USD\nВведите "Да" или "Нет":\n')).lower()
    if choice == 'нет':
        pprint(vacancy_list)
        break
    elif choice == 'да':
        for el in vacancy_list:
            if el['USD']:
                pprint(el)
        break
    else:
        print('Ответ введен некорректно. Попробуйте еще раз.')
