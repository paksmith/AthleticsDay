from flask import Flask, render_template, redirect, request
import pymysql

app = Flask(__name__)

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app

def create_connection():
    return pymysql.connect(  
        host = '127.0.0.1',
        user = 'root',
        password = '13com',
        db = 'AthleticsDay',
        charset = 'utf8mb4',
        cursorclass = pymysql.cursors.DictCursor
    )

@app.route('/')
def index():
    connection = create_connection()
    with connection.cursor() as cursor:
        sql = "SELECT eventID, eventName FROM tblEvents;"
        cursor.execute(sql)
        events = cursor.fetchall()
        connection.close()
    return render_template("index.html", events = events)

if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)
