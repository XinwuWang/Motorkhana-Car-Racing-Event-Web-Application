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
    connection = getCursor()
    connection.execute("SELECT driver_id, first_name, surname FROM driver")
    drivers_info_unsorted = connection.fetchall()
    drivers_info = sorted(drivers_info_unsorted, key=lambda x: (x[1], x[2]))
    return render_template("base.html", drivers_info=drivers_info)


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


# @app.route("/runinfo")
# def runinfo():
#     connection = getCursor()
#     check_column_exists = """SELECT COUNT(*)
#     FROM information_schema.columns
#     WHERE table_schema='motorkhana'
#     AND table_name='run'
#     AND column_name='run_total'""".format("motorkhana", "run", "run_total")
#     connection.execute(check_column_exists)
#     if not connection.fetchone()[0] > 0:
#         add_column = "ALTER TABLE run ADD run_total FLOAT;"
#         connection.execute(add_column)

#     connection.execute("SELECT * FROM run")
#     runsList = connection.fetchall()
#     for run in runsList:
#         if run[3] is not None:
#             run_total = run[3] + (run[4] or 0) * 5 + (run[5] or 0) * 10
#             connection.execute(
#                 "UPDATE run SET run_total = %s WHERE dr_id= %s AND crs_id = %s AND run_num= %s",
#                 (run_total, run[0], run[1], run[2])
#             )
#         else:
#             run_total = None
#             connection.execute(
#                 "UPDATE run SET run_total = %s WHERE dr_id= %s AND crs_id = %s AND run_num= %s",
#                 (run_total, run[0], run[1], run[2])
#             )

#     # connection.execute("""SELECT d.driver_id, d.first_name, d.surname, c.model, c.drive_class
#     #                    FROM driver d
#     #                    LEFT JOIN car c
#     #                    ON d.car=c.car_num""")
#     # drivers_info = connection.fetchall()
#     print(runsList)
#     # print(drivers_info)
#     return render_template("runsinfo.html", runs_list=runsList)


@app.route("/driver/<int:driver_id>")
def driver_run_detail(driver_id):
    connection = getCursor()

    # Add the run_total column to the database if the column does not exist
    check_column_exists = """SELECT COUNT(*)
    FROM information_schema.columns
    WHERE table_schema='motorkhana'
    AND table_name='run'
    AND column_name='run_total'""".format("motorkhana", "run", "run_total")
    connection.execute(check_column_exists)
    if not connection.fetchone()[0] > 0:
        add_column = "ALTER TABLE run ADD run_total FLOAT;"
        connection.execute(add_column)

    # If the run_total column exists, execute query to get the run total results of each run
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

    # Select a driver's information and his/her all runs' details
    connection.execute("""SELECT d.driver_id, d.first_name, d.surname, c.model, c.drive_class
                       FROM driver d
                       LEFT JOIN car c
                       ON d.car=c.car_num
                       WHERE d.driver_id = %s""", (driver_id,))
    driver = connection.fetchone()

    # Get a list of all the courses' information
    connection.execute("SELECT * FROM course;")
    courses = connection.fetchall()

    return render_template("driver_detail.html", driver_id=driver_id, driver=driver, runsList=runsList, courses=courses)
