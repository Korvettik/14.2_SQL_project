from flask import Flask, render_template, request, jsonify
import json
import sqlite3

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


# netflix.db

# Структура таблицы
# -----------------------
# show_id — id тайтла
# type — фильм или сериал
# title — название
# director — режиссер
# cast — основные актеры
# country — страна производства
# date_added — когда добавлен на Нетфликс
# release_year — когда выпущен в прокат
# rating — возрастной рейтинг
# duration — длительность
# duration_type — минуты или сезоны
# listed_in — список жанров и подборок
# description — краткое описание
# -----------------------


# Главная страница домашки
@app.route('/', methods=['GET', 'POST'])
def main_page():
    return render_template('index.html')


# 1 Поиск по названию
@app.route('/name/', methods=['GET', 'POST'])
def name_page(json_str=False):
    s = request.args.get('s')
    with sqlite3.connect("netflix.db") as con:
        cur = con.cursor()

        sqlite_query = f"""
            SELECT "title", "country", "release_year", "rating", "description"
            FROM "netflix"
            WHERE "title" LIKE "%{s}%"
            ORDER BY "title"
            """
        rows = cur.execute(sqlite_query).fetchall()  # вернет список кортежей

    # создаем JSON объект
    data = list()
    for row in rows:
        new_row = {"title": row[0],
                   "country": row[1],
                   "release_year": row[2],
                   "rating": row[3],
                   "description": row[4]}
        data.append(new_row)

    return jsonify(data)


# 2 Поиск по диапазону лет выпуска
@app.route('/interval/', methods=['GET', 'POST'])
def interval_page():
    s = request.args.get('s')
    interval = s.split('-')
    with sqlite3.connect("netflix.db") as con:
        cur = con.cursor()

        sqlite_query = f"""
            SELECT "title", "release_year"
            FROM "netflix"
            WHERE "release_year" BETWEEN "{interval[0]}" AND "{interval[1]}"
            ORDER BY "release_year"
            LIMIT 100
            """
        rows = cur.execute(sqlite_query).fetchall()  # вернет список кортежей

    # создаем JSON объект
    data = list()
    for row in rows:
        new_row = {"title": row[0],
                   "release_year": row[1]}
        data.append(new_row)

    return jsonify(data)


# 3 Поиск по рейтингу   ----------------------------------------------
@app.route('/rating/', methods=['GET', 'POST'])
def rating_page():
    s = request.args.get('s')
    res = ""
    if s == "children":
        res = "\"G\""
    elif s == "family":
        res = "\"G\", \"PG\", \"PG-13\""
    elif s == "adult":
        res = "\"R\" ,  \"NC-17\""

    with sqlite3.connect("netflix.db") as con:
        cur = con.cursor()

        sqlite_query = f"""
            SELECT "title", "rating", "description"
            FROM "netflix"
            WHERE "rating" IN ({res})
            ORDER BY "title"
            """
        print(sqlite_query)
        rows = cur.execute(sqlite_query).fetchall()  # вернет список кортежей

    # создаем JSON объект
    data = list()
    for row in rows:
        new_row = {"title": row[0],
                   "rating": row[1],
                   "description": row[2]}
        data.append(new_row)

    return jsonify(data)


# 4 Поиск по жанру, выводит 10 самых свежих фильмов
@app.route('/genre/', methods=['GET', 'POST'])
def genre_page():
    s = request.args.get('s')
    with sqlite3.connect("netflix.db") as con:
        cur = con.cursor()

        sqlite_query = f"""
            SELECT "title", "description"
            FROM "netflix"
            WHERE "listed_in" LIKE "%{s}%"
            ORDER BY "release_year" DESC
            LIMIT 10
            """
        rows = cur.execute(sqlite_query).fetchall()  # вернет список кортежей

    # создаем JSON объект
    data = list()
    for row in rows:
        new_row = {"title": row[0],
                   "description": row[1]}
        data.append(new_row)

    return jsonify(data)


# 5 Поиск актеров, кто играет в паре с актерами больше 2х раз
# Rose McIver - Ben Lamb
# Jack Black - Dustin Hoffman
@app.route('/actors/', methods=['GET', 'POST'])
def actors_page():
    s = request.args.get('s')
    with sqlite3.connect("netflix.db") as con:
        cur = con.cursor()
        actor_name = s.split(' - ')
        print(actor_name)
        sqlite_query = f"""
                SELECT "cast"
                FROM "netflix"
                WHERE "cast" LIKE "%{actor_name[0]}%"
                AND "cast" LIKE "%{actor_name[1]}%"
                ORDER BY "title"
                """
        rows = cur.execute(sqlite_query).fetchall()  # вернет список кортежей актеров
        print(rows)
    rows_dict = dict()
    for row in rows:  # row - кортэж с 1 строкой - актеров 1 фильма
        for string in row:
            actors_list = string.split(", ")
            for actor in actors_list:
                if actor not in rows_dict.keys():
                    rows_dict[actor] = 1
                else:
                    rows_dict[actor] += 1
    print(rows_dict)

    rows_list = list()
    for actor in rows_dict.keys():
        if actor not in actor_name:
            if rows_dict[actor] >= 2:
                rows_list.append(actor)

    return jsonify(rows_list)


# 6 Вывод картин по фильтру
@app.route('/filter/', methods=['GET', 'POST'])
def filter_page():
    s = request.args.get('s')
    filter = s.split('-')
    print(filter)

    with sqlite3.connect("netflix.db") as con:
        cur = con.cursor()
        # Movie-2016-Dramas
        sqlite_query = f"""
            SELECT "title", "description"
            FROM "netflix"
            WHERE "type" = "{filter[0]}"
            AND "release_year" = {int(filter[1])} 
            AND "listed_in" LIKE "%{filter[2]}%"
            ORDER BY "title"
            """
        rows = cur.execute(sqlite_query).fetchall()  # вернет список кортежей

    # создаем JSON объект
    data = list()
    for row in rows:
        new_row = {"title": row[0],
                   "description": row[1]}
        data.append(new_row)

    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)
