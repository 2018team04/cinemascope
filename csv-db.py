import sqlite3
import csv

f=open('movies.csv','r') # open the csv data file
next(f, None) # skip the header row
reader = csv.reader(f)

sql = sqlite3.connect('movies.db')
cur = sql.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS movies
            (context text, response text, score real)''') # create the table if it doesn't already exist

for row in reader:
	cur.execute("INSERT INTO utterances VALUES (?, ?, ?)", row)

f.close()
sql.commit()
sql.close()
