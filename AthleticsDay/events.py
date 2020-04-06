from flask import Flask, render_template, redirect, request, session
from hashlib import md5

from __main__ import app
from utils import *

@app.route('/eventsChoose')
def eventsChoose():
    print("eventsChoose")
    connection = create_connection()
    with connection.cursor() as cursor:
        sql = "SELECT eventID, eventName FROM tblEvents;"
        cursor.execute(sql)
        events = cursor.fetchall()
        connection.close()
    return render_template("eventsChoose.html", events = events)
