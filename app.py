from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
import re
from datetime import datetime
import mysql.connector
from mysql.connector import FieldType
import connect


app = Flask(__name__)

dbconn = None
connection = None


def getCursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(user=connect.dbuser,
                                         password=connect.dbpass, host=connect.dbhost,
                                         database=connect.dbname, autocommit=True)
    dbconn = connection.cursor()
    return dbconn


@app.route("/")
def home():
    return render_template("base.html")


@app.route("/listdrivers")
def listdrivers():
    connection = getCursor()
    connection.execute("""SELECT driver_id, first_name, surname, date_of_birth, age, caregiver, car.model, car.drive_class
                       FROM driver
                       LEFT JOIN car
                       ON driver.car = car.car_num;""")
    driverList = connection.fetchall()
    return render_template("driverlist.html", driver_list=driverList)


@app.route("/listcourses")
def listcourses():
    connection = getCursor()
    connection.execute("SELECT * FROM course")
    courseList = connection.fetchall()
    return render_template("courselist.html", course_list=courseList)


@app.route("/graph")
def showgraph():
    connection = getCursor()
    # Insert code to get top 5 drivers overall, ordered by their final results.
    # Use that to construct 2 lists: bestDriverList containing the names, resultsList containing the final result values
    # Names should include their ID and a trailing space, eg '133 Oliver Ngatai '

    return render_template("top5graph.html", name_list=bestDriverList, value_list=resultsList)


@app.route("/runinfo")
def runinfo():
    connection = getCursor()
    check_column_exists = """SELECT COUNT(*)
    FROM information_schema.columns 
    WHERE table_schema='motorkhana' 
    AND table_name='run' 
    AND column_name='run_total'""".format("motorkhana", "run", "run_total")
    connection.execute(check_column_exists)
    if not connection.fetchone()[0] > 0:
        add_column = "ALTER TABLE run ADD run_total FLOAT;"
        connection.execute(add_column)

    connection.execute("SELECT * FROM run")
    runsList = connection.fetchall()
    for run in runsList:
        if run[3] is not None:
            run_total = run[3] + (run[4] or 0) * 5 + (run[5] or 0) * 10
            connection.execute(
                "UPDATE run SET run_total = %s WHERE dr_id= %s AND crs_id = %s AND run_num= %s",
                (run_total, run[0], run[1], run[2])
            )
        else:
            run_total = None
            connection.execute(
                "UPDATE run SET run_total = %s WHERE dr_id= %s AND crs_id = %s AND run_num= %s",
                (run_total, run[0], run[1], run[2])
            )
    print(runsList)
    return render_template("runsinfo.html", runs_list=runsList)
