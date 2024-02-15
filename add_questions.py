import csv
import mysql.connector as mysql

mycon = mysql.connect(host="localhost", user="root", password="greenskrulls", database="staladb")
cursor = mycon.cursor()

csv_file_path = 'stala_questions.csv'

cursor.execute("SHOW TABLES LIKE 'questions'")
table_exists = cursor.fetchone()

if not table_exists:
    cursor.execute('''
        CREATE TABLE questions (
            question NVARCHAR(255),
            opt1 NVARCHAR(255),
            opt2 NVARCHAR(255),
            opt3 NVARCHAR(255),
            opt4 NVARCHAR(255),
            answer NVARCHAR(255)
        )
    ''')
    mycon.commit()

with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile)
    next(csvreader)  
    for row in csvreader:
        question, opt1, opt2, opt3, opt4, answer = row
        cursor.execute('INSERT INTO questions VALUES (%s, %s, %s, %s, %s, %s)',
                       (question, opt1, opt2, opt3, opt4, answer))
        mycon.commit()
      
cursor.execute("SHOW TABLES LIKE 'player'")
table_exists = cursor.fetchone()

if not table_exists:      
    cursor.execute('''
        CREATE TABLE player (
          usrname VARCHAR(255),
          passwd VARCHAR(255),
          email VARCHAR(255),
          datee DATE,
          score INT DEFAULT 0,
          played INT DEFAULT 0
        )
    ''')
mycon.commit()

mycon.close()

print("Data uploaded successfully.")
