from flask import Flask, render_template, redirect, request, session
from hashlib import md5

from __main__ import app
from utils import *

@app.route('/eventsChoose', methods = ["GET", "POST"])
def eventsChoose():
    if request.method == "POST":
        #Form has been submitted. Check whether they are adding or removing an entry and process accordingly
        if request.form["submit"] == "Add":
            connection = create_connection()
            with connection.cursor() as cursor:
                sql = "INSERT INTO tblEntries(userID, eventID) VALUES (%s, %s);"
                vals = (session["userID"], request.form["eventID"])
                cursor.execute(sql, vals)
                connection.commit()
                connection.close()
        elif  request.form["submit"] == "Remove":
            connection = create_connection()
            with connection.cursor() as cursor:
                sql = "DELETE FROM tblEntries WHERE userID = %s AND eventID = %s;"
                vals = (session["userID"], request.form["eventID"])
                cursor.execute(sql, vals)
                connection.commit()
                connection.close()

    #Display events. Need to pass all events to template, as well as all events that 
    #user is currently entered for.
    connection = create_connection()
    with connection.cursor() as cursor:
        sql = "SELECT tblevents.eventID, eventName FROM tblevents;"
        cursor.execute(sql)
        events = cursor.fetchall()
        sql = "SELECT eventID, userID FROM tblEntries WHERE userID = %s;"
        vals = session["userID"]
        cursor.execute(sql, vals)
        enteredEvents = cursor.fetchall()
        connection.close()

    return render_template("eventsChoose.html", events = events, enteredEvents = enteredEvents)
