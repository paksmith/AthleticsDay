from flask import Flask, render_template, redirect, request, session
from hashlib import md5

from __main__ import app
from utils import *

#TODO shouldn't need to define constants twice...
ROLE_USER = 1
ROLE_ADMIN = 2
ROLE_TEACHER = 3

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

@app.route('/eventsTickCompleted', methods = ["GET", "POST"])
def eventsTickCompleted():
    if request.method == "POST":
        connection = create_connection()
        with connection.cursor() as cursor:

            #First set all values to False for this user
            sql = "UPDATE tblentries SET completed = False WHERE userID = %s;"
            vals = (session["userID"])
            cursor.execute(sql, vals)
            connection.commit()

            #Then set True for all that were ticked in form
            completedEvents = request.form.getlist("completed")
            for event in completedEvents:     
                sql = "UPDATE tblentries SET completed = True WHERE entryID = %s;"
                vals = (event)
                cursor.execute(sql, vals)
                connection.commit()
        connection.close()

    #Display events for this user.
    connection = create_connection()
    with connection.cursor() as cursor:
        sql = "SELECT tblevents.eventID, eventName, completed, entryID FROM tblentries INNER JOIN tblevents ON tblevents.eventID = tblentries.eventID WHERE tblentries.userID = %s;"
        vals = session["userID"]
        cursor.execute(sql, vals)
        enteredEvents = cursor.fetchall()
        connection.close()

    return render_template("eventsTickCompleted.html", enteredEvents = enteredEvents)


@app.route("/eventsAdd", methods=["GET", "POST"])
def eventsAdd():
    #First mke sure we have the rights to do this stuff
    if not session["roleID"] == ROLE_ADMIN:
        return redirect("/")
    else:
        if request.method == "POST":
            #Get values from form, insert into tblEvents.
            eventName = request.form["eventName"]

            connection = create_connection()
            with connection.cursor() as cursor:
                sql = "INSERT INTO tblevents(eventName) VALUES(%s)"
                vals = (eventName)
                cursor.execute(sql, vals)
                connection.commit()
                connection.close()

        return render_template("eventsAdd.html")

@app.route("/eventEdit", methods=["GET", "POST"])
def eventEdit():
    #First mke sure we have the rights to do this stuff
    if not session["roleID"] == ROLE_ADMIN:
        return redirect("/")
    else:
        if request.method == "POST":
            eventID = request.form["eventID"]
            eventName = request.form["eventName"]
            connection = create_connection()
            with connection.cursor() as cursor:
                sql = "UPDATE tblevents SET eventName=%s WHERE eventID=%s"
                vals = (eventName, eventID)
                cursor.execute(sql, vals)
                connection.commit()
                connection.close()
            return redirect("/events")
        else:
            eventID = request.args["eventID"]
            connection = create_connection()
            with connection.cursor() as cursor:
                sql  = "SELECT eventID, eventName FROM tblevents WHERE eventID = %s;"
                vals = (eventID)
                cursor.execute(sql, vals)
                event = cursor.fetchone()
                connection.close()
            return render_template("eventEdit.html", event = event)

@app.route("/events")
def events():
    if session["roleID"] == ROLE_ADMIN:
        connection = create_connection()
        with connection.cursor() as cursor:
            sql  = "SELECT eventID, eventName FROM tblEvents;"
            cursor.execute(sql)
            events = cursor.fetchall()
            connection.close()
        return render_template("events.html", events = events)
    else:
        return redirect("/")