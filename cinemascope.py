from flask import Flask, render_template, request
import pandas as pd
import numpy as np
from flask_table import Table, Col
from flask_mysqldb import MySQL
import json

from werkzeug.utils import redirect




app = Flask(__name__)

# Configure db

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'cinemascope'

mysql = MySQL(app)


# Welcome Page
@app.route("/")
def index():
    return render_template('index.html')


# Rating Page
@app.route("/rating", methods=["GET", "POST"])
def genre():
    if request.method == "POST":
        return execute()
    return render_template('genre.html')


@app.route("/", methods=["GET", "POST"])
def execute():
    if request.method == 'POST':
        # reading the original dataset
        movies = pd.read_csv('movies.csv', encoding=('latin-1'))

        # separating genres for each movie
        movies = pd.concat([movies, movies.genre.str.get_dummies(sep='|')], axis=1)

        # dropping variables to have a dummy 1-0 matrix of movies and their genres

        categories = movies.drop(['title', 'genre', 'IMAX', 'id', 'Film-Noir'], axis=1)

        # initializing user preference list which will contain user ratings
        preferences = []

        # reading rating values given by user in the front-end
        Action = request.form.get('Action')
        Adventure = request.form.get('Adventure')
        Animation = request.form.get('Animation')
        Children = request.form.get('Children')
        Comedy = request.form.get('Comedy')
        Crime = request.form.get('Crime')
        Documentary = request.form.get('Documentary')
        Drama = request.form.get('Drama')
        Fantasy = request.form.get('Fantasy')
        # FilmNoir = request.form.get('FilmNoir')
        Horror = request.form.get('Horror')
        Musical = request.form.get('Musical')
        Mystery = request.form.get('Mystery')
        Romance = request.form.get('Romance')
        SciFi = request.form.get('SciFi')
        Thriller = request.form.get('Thriller')
        War = request.form.get('War')
        Western = request.form.get('Western')

        # inserting each rating in a specific position based on the movie-genre matrix
        preferences.insert(0, int(Action))
        preferences.insert(1, int(Adventure))
        preferences.insert(2, int(Animation))
        preferences.insert(3, int(Children))
        preferences.insert(4, int(Comedy))
        preferences.insert(5, int(Crime))
        preferences.insert(6, int(Documentary))
        preferences.insert(7, int(Drama))
        preferences.insert(8, int(Fantasy))
        # preferences.insert(9, int(FilmNoir))
        preferences.insert(10, int(Horror))
        preferences.insert(11, int(Musical))
        preferences.insert(12, int(Mystery))
        preferences.insert(13, int(Romance))
        preferences.insert(14, int(SciFi))
        preferences.insert(15, int(War))
        preferences.insert(16, int(Thriller))
        preferences.insert(17, int(Western))

        # This funtion will get each movie score based on user's ratings through dot product
        def get_score(a, b):
            return np.dot(a, b)

        # Generating recommendations based on top score movies
        def recommendations(X, n_recommendations):
            movies['score'] = get_score(categories, preferences)
            return movies.sort_values(by=['score'], ascending=False)['id'][:n_recommendations]

        movie_list = recommendations(preferences, 10)
        movieid = list(movie_list)
        cur = mysql.connection.cursor()
        sql_insert_query = """ INSERT INTO myrating(movie_id) 
                       VALUES (%s) """
        cur.executemany(sql_insert_query, movieid)

        mysql.connection.commit()

    return redirect("recommendation")


@app.route("/recommendation", methods=["GET", "POST"])
def recommendation():
    cur = mysql.connection.cursor()
    sql_output_query = """ SELECT *
                            FROM  myrating,movie
                            WHERE  myrating.movie_id  =
                            movie.movie_id ORDER BY id DESC LIMIT 10; """
    output = cur.execute(sql_output_query)

    if output > 0:
        result = cur.fetchall()


        return render_template('recommendation.html', result=result)
    return 'not found'


if __name__ == '__main__':
    app.run(debug=True)
