from flask import Flask, render_template, redirect, request, session
from hashlib import md5
import pymysql

app = Flask(__name__)

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app

ROLE_USER = 1
ROLE_ADMIN = 2
ROLE_TEACHER = 3

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

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        userName = request.form["userName"]
        password = request.form["password"]
        password = md5(password.encode()).hexdigest()
        connection = create_connection()
        with connection.cursor() as cursor:
            sql = "SELECT * FROM tblusers WHERE userName = %s AND password = %s"
            vals = (userName, password)
            cursor.execute(sql, vals)
            users = cursor.fetchall()
        connection.close()
        if len(users) == 0:
            #Login failed
            return render_template("login.html")
        else:
            #Login succeeded'
            user = users[0]
            session['userName'] = user['roleID']
            session['firstName'] = user['firstName']
            session['lastName'] = user['lastName']
            session["loggedIn"] = True
            session["roleId"] = user['roleID']
            return redirect('/')
    else:
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        #Get values from form, insert into tblUsers.
        #TODO add validation (such as check that username is not already taken)
        userName = request.form["userName"]
        firstName = request.form["firstName"]
        lastName = request.form["lastName"]
        password = request.form["password"]
        password = md5(password.encode()).hexdigest()
        connection = create_connection()
        with connection.cursor() as cursor:
            sql = "INSERT INTO tblusers(userName, firstName, lastName, password, roleID) VALUES(%s, %s, %s, %s, %s)"
            vals = (userName, firstName, lastName, password, ROLE_USER)
            cursor.execute(sql, vals)
            connection.commit()
            connection.close()
        return redirect("/login")
    else:
        return render_template("register.html")

if __name__ == '__main__':
    import os
    app.secret_key = os.urandom(12)
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)
