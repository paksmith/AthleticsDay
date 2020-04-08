from flask import Flask, render_template, redirect, request, session
from hashlib import md5

app = Flask(__name__)

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app

ROLE_USER = 1
ROLE_ADMIN = 2
ROLE_TEACHER = 3


from events import *
from utils import *

@app.route('/')
def index():
    if session.get("loggedIn"):
        if session["loggedIn"]:
            return redirect("/eventsChoose")
    return redirect("/login")

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
            #Login succeeded
            user = users[0]
            session['userName'] = user['roleID']
            session['firstName'] = user['firstName']
            session['lastName'] = user['lastName']
            session["loggedIn"] = True
            session["roleID"] = user['roleID']
            session['userID'] = user['userID']
            return redirect('/')
    else:
        return render_template("login.html")

@app.route("/users")
def manage_users():
    if session["roleID"] == ROLE_ADMIN:
        connection = create_connection()
        with connection.cursor() as cursor:
            sql  = "SELECT userID, userName, firstName, lastName, tblUsers.roleID, roleName FROM tblUsers LEFT JOIN tblRoles ON tblUsers.roleID = tblRoles.roleID;"
            cursor.execute(sql)
            users = cursor.fetchall()
            connection.close()
        return render_template("users.html", users = users)
    else:
        return redirect("/")
  
@app.route("/edituser", methods=["GET", "POST"])
def edit_users():
    #First mke sure we have the rights to do this stuff
    if not session["roleID"] == ROLE_ADMIN:
        return redirect("/")
    else:
        if request.method == "POST":
            userID = request.form["userID"]
            userName = request.form["userName"]
            firstName = request.form["firstName"]
            lastName = request.form["lastName"]
            roleID = request.form["roleID"]
            connection = create_connection()
            with connection.cursor() as cursor:
                sql = "UPDATE tblusers SET userName=%s, firstName=%s, lastName=%s, roleID=%s WHERE userID=%s"
                vals = (userName, firstName, lastName, roleID, userID)
                cursor.execute(sql, vals)
                connection.commit()
                connection.close()
            return redirect("/users")
        else:
            userID = request.args["userID"]
            connection = create_connection()
            with connection.cursor() as cursor:
                sql  = "SELECT userID, userName, firstName, lastName, tblUsers.roleID, roleName FROM tblUsers LEFT JOIN tblRoles ON tblUsers.roleID = tblRoles.roleID WHERE userID = %s;"
                vals = (userID)
                cursor.execute(sql, vals)
                user = cursor.fetchone()
                connection.close()
            return render_template("edituser.html", user = user)

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
