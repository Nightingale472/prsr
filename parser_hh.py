import requests
import psycopg2
import json
from pywebio import input, output, start_server

def get_vacancies(vacancy):
    url = "https://api.hh.ru/vacancies"
    params = {
        "text": vacancy,
        "area": 1, #(1 для поиска по Москве)
        "per_page": 20,
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        vacancies = data.get("items", [])
        num_vacancies = len(vacancies)
        try:
            json_data = response.json()

            conn = psycopg2.connect(
                dbname='postgres',
                user='postgres',
                password='1234',
                host='127.0.0.1',
                port='5432'
            )

            cur = conn.cursor()

            cur.execute('''
                CREATE TABLE IF NOT EXISTS json_table (
                    id SERIAL PRIMARY KEY,
                    data JSONB
                )
            ''')

            cur.execute('''
                INSERT INTO json_table (data) VALUES (%s)
            ''', [json.dumps(json_data)])

            conn.commit()
            cur.close()
            conn.close()
        except Exception:
            print("Не получилось создать бд.")


        if num_vacancies > 0:
            for i, vacancy in enumerate(vacancies):
                vacancy_id = vacancy.get("id")
                vacancy_name = vacancy.get("name")
                vacancy_url = vacancy.get("alternate_url")
                employment = vacancy.get("employment", {}).get("name")
                company_name = vacancy.get("employer", {}).get("name")
                output.put_text(f"ID вакансии: {vacancy_id}")
                output.put_text(f"Название вакансии: {vacancy_name}")
                output.put_text(f"Название компании: {company_name}")
                output.put_text(f"Тип занятости: {employment}")
                output.put_text(f"Ссылка на вакансию: {vacancy_url}")
                output.put_text("")

                if i < num_vacancies - 1:
                    output.put_text("---------------------")
        else:
            output.put_text("Нет вакансий.")
    else:
        output.put_text(f"Ошибка с кодом: {response.status_code}")


def search_vacancies():
    search = input.input("Введите название вакансии:", type=input.TEXT)
    output.clear()
    output.put_text(f"Поиск вакансий по значению {search}")
    get_vacancies(search)


if __name__ == '__main__':
    start_server(search_vacancies, port=8080)