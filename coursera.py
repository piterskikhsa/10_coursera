import re
import requests
import sys
from bs4 import BeautifulSoup
from openpyxl import Workbook


def get_page_data(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'}
    response = requests.get(url, headers)
    return response


def get_courses_list(url, limit_url=20):
    xml_string = get_page_data(url).content
    soup = BeautifulSoup(xml_string, 'lxml')
    return [course_url.text for course_url in soup.find_all('loc', limit=limit_url)]


def get_course_info(course_url):
    # вытащить оттуда название, язык, ближайшую дату начала, количество недель и среднюю оценку.
    response = get_page_data(course_url)
    if response.ok:
        soup = BeautifulSoup(response.content, 'lxml')
        title = soup.find('h1', {'class': 'title display-3-text'}).text
        language = soup.find('div', {'class': 'rc-Language'}).text
        course_rating = soup.find('div', {'class': 'ratings-text bt3-hidden-xs'})
        if course_rating:
            course_rating = course_rating.text
            course_rating = re.findall(r'\d+.\d+', course_rating)[0]
        start_date = soup.find('div', {'class': 'startdate rc-StartDateString caption-text'}).find('span').text
        return {'title': title, 'language': language, 'course_rating': course_rating, 'start_date': start_date}


def output_courses_info_to_xlsx(filepath, courses_info_list):
    wb = Workbook()
    ws = wb.active
    ws.title = 'Coursera'
    ws.append([key for key in courses_info_list[0].keys()])
    for course_info in courses_info_list:
        ws.append([info for info in course_info.values()])

    wb.save(filepath)
    print('Файл успешно сохранен')


def main():
    url = 'https://www.coursera.org/sitemap~www~courses.xml'
    courses_url_list = get_courses_list(url)
    if courses_url_list:
        print('Обработка данных')
        courses_info_list = []
        for course_url in courses_url_list:
            course_info = get_course_info(course_url)
            courses_info_list.append(course_info)

        output_courses_info_to_xlsx(file_path, courses_info_list)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = input('Укажите путь к файлу: ')

    main()
