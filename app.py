from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import session
import re
from datetime import datetime
import mysql.connector
from mysql.connector import FieldType
import connect


app = Flask(__name__)
# Set a secret key for the session that will be used later.
app.secret_key = "motorkhana_fast"

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

    # Get drivers' names and add them to the dropdown box
    connection.execute("SELECT driver_id, first_name, surname FROM driver")
    drivers_info_unsorted = connection.fetchall()
    drivers_info = sorted(drivers_info_unsorted, key=lambda x: (x[1], x[2]))
    print(drivers_info)
    return render_template("base.html", drivers_info=drivers_info)


@app.route("/listdrivers")
def listdrivers():
    connection = getCursor()
    connection.execute("""SELECT driver_id, first_name, surname, date_of_birth, age, caregiver, car.model, car.drive_class
                       FROM driver
                       LEFT JOIN car
                       ON driver.car = car.car_num;""")
    driverList_unsorted = connection.fetchall()
    driverList = sorted(driverList_unsorted, key=lambda x: (x[2], x[1]))

    # Create the 'drivers_info' list so on this route users can access the dropdown box in the navigation bar.
    # Data of this list will be passed to the navigation bar.
    drivers_info = sorted([(driver[0], driver[1], driver[2])
                          for driver in driverList], key=lambda x: (x[1], x[2]))

    return render_template("driverlist.html", driver_list=driverList, drivers_info=drivers_info)


@app.route("/listcourses")
def listcourses():
    connection = getCursor()

    # Get data from the course table
    connection.execute("SELECT * FROM course")
    courseList = connection.fetchall()

    # Get drivers' names and add them to the dropdown box
    connection.execute("SELECT driver_id, first_name, surname FROM driver")
    drivers_info_unsorted = connection.fetchall()
    drivers_info = sorted(drivers_info_unsorted, key=lambda x: (x[1], x[2]))

    return render_template("courselist.html", course_list=courseList, drivers_info=drivers_info)


@app.route("/driver/<int:driver_id>")
def driver_run_detail(driver_id):
    connection = getCursor()

    # Get runs list
    connection.execute("SELECT * FROM run")
    runsList = connection.fetchall()

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

    # Get drivers' names and add them to the dropdown box
    connection.execute("SELECT driver_id, first_name, surname FROM driver")
    drivers_info_unsorted = connection.fetchall()
    drivers_info = sorted(drivers_info_unsorted, key=lambda x: (x[1], x[2]))

    return render_template("driver_detail.html", driver_id=driver_id, driver=driver, runsList=runsList, courses=courses, drivers_info=drivers_info)


@app.route("/overallresults")
def overall_results():
    connection = getCursor()

    # Get drivers' ID, first name, last name, and car models
    connection.execute("""SELECT d.driver_id, d.first_name, d.surname, d.age, c.model
                       FROM driver d
                       LEFT JOIN car c
                       ON d.car=c.car_num""")

    driver_info_unsorted = connection.fetchall()
    driver_info = sorted(driver_info_unsorted, key=lambda x: (x[2], x[1]))

    # Get 6 course times for each driver
    connection.execute("SELECT dr_id, crs_id, run_num, run_total FROM run")
    runs_info = connection.fetchall()

    # Compare two run_totals and keep the best one
    # Create an empty dictionary to store the best run_totals for each (dr_id, crs_id) combination
    best_run_totals = {}

    # Comapre two runtotals
    for run in runs_info:
        # # If run_total is None, set it to 'dnf'
        # if run[3] is None:
        #     run)[3] = 'dnf'

        # Check if (dr_id, crs_id) is in the dictionary
        key = (run[0], run[1])
        if key not in best_run_totals:
            # If not, add the current run_total
            best_run_totals[key] = run[3]
        else:
            # if yes, update the value to the maximum of current and stored run_total
            if best_run_totals[key] is not None and run[3] is not None:
                # Use the 'min()' function to get the best result
                best_run_totals[key] = min(best_run_totals[key], run[3])
            elif best_run_totals[key] is None:
                best_run_totals[key] = run[3]

    # Convert the dictionary back to a list of tuples
    course_time = [(key[0], key[1], best_run_totals[key])
                   for key in best_run_totals]

    driver_info_dic = {item[0]: {"dr_id": item[0],
                                 "name": item[2] + ", " + item[1],
                                 "age": item[3],
                                 "model": item[4]}
                       for item in driver_info
                       }

    # Add 6 course time to each driver
    for course in course_time:
        if course[0] in driver_info_dic:
            driver_info_dic[course[0]][course[1]] = course[2]

    for key in driver_info_dic.keys():
        overall_result = 0
        for course_name in ["A", "B", "C", "D", "E", "F"]:
            if driver_info_dic[key][course_name] is not None:
                overall_result += driver_info_dic[key][course_name]
            else:
                driver_info_dic[key][course_name] = "dnf"
                overall_result = "NQ"
        driver_info_dic[key]["overall"] = round(
            overall_result, 2) if overall_result != "NQ" else "NQ"

    # Use the lambda function here to sort the overall results from best to worst, and put NQ at the bottom
    sorted_overall = dict(sorted(driver_info_dic.items(),
                                 key=lambda item: (float(item[1]["overall"]) if item[1]["overall"] != "NQ" else float("inf"))))
    print(sorted_overall)
    # Store the overall resutls dictionary in the Flask session object that can be retrieved in the "graph" route later.
    session["sorted_overall"] = sorted_overall

    # Create the 'drivers_info' list so on this route users can access the dropdown box in the navigation bar.
    # Data of this list will be passed to the navigation bar.
    drivers_info = sorted([(driver[0], driver[1], driver[2])
                          for driver in driver_info], key=lambda x: (x[1], x[2]))

    return render_template("overall_results.html", sorted_overall=sorted_overall, drivers_info=drivers_info)


@app.route("/graph")
def showgraph():
    connection = getCursor()
    # Get drivers' names and add them to the dropdown box
    connection.execute("SELECT driver_id, first_name, surname FROM driver")
    drivers_info_unsorted = connection.fetchall()
    drivers_info = sorted(drivers_info_unsorted, key=lambda x: (x[1], x[2]))

    # Retrieve the dictionary from the session
    sorted_overall = session.get("sorted_overall", {})
    # Sort the overall results dictionary from best to worst
    sorted_overall_dict = dict(sorted(sorted_overall.items(),
                                      key=lambda item: (float(item[1]["overall"]) if item[1]["overall"] != "NQ" else float("inf"))))

    # Insert code to get top 5 drivers overall, ordered by their final results.
    top5_drivers = list(sorted_overall_dict.values())[:5]

    # Use that to construct 2 lists: bestDriverList containing the names, resultsList containing the final result values
    # Names should include their ID and a trailing space, eg '133 Oliver Ngatai '
    bestDriverList = [
        f"{driver['dr_id']} {driver['name']} " for driver in top5_drivers]
    resultsList = [driver["overall"] for driver in top5_drivers]

    return render_template("top5graph.html", name_list=bestDriverList, value_list=resultsList, drivers_info=drivers_info)


@app.route("/admin")
def admin_home():
    return render_template("admin_base.html")


@app.route("/admin/junior_list")
def junior_list():
    connection = getCursor()
    connection.execute(
        "SELECT driver_id, first_name, surname, date_of_birth, age, caregiver FROM driver")
    all_drivers = connection.fetchall()

    junior_drivers_unsorted = []
    for driver in all_drivers:
        if driver[4] and 12 <= driver[4] <= 25:
            if driver[4] <= 16:
                for drivers in all_drivers:
                    if drivers[0] == driver[5]:
                        junior_drivers_unsorted.append(
                            (driver[0], driver[1], driver[2], driver[3], driver[4], drivers[1] + " " + drivers[2]))
            else:
                junior_drivers_unsorted.append(
                    (driver[0], driver[1], driver[2], driver[3], driver[4], None))
    print(junior_drivers_unsorted)
    junior_drivers = sorted(junior_drivers_unsorted,
                            key=lambda x: (x[4], x[2]), reverse=True)
    print(junior_drivers)

    return render_template("juniorlist.html", junior_drivers=junior_drivers)


@app.route("/admin/search_results", methods=["GET", "POST"])
def search():
    connection = getCursor()
    if request.method == "POST":
        input = request.form.get("search_query")
        connection.execute("""SELECT d.driver_id, d.first_name, d.surname, d.age, c.model, c.drive_class
                       FROM driver d
                       LEFT JOIN car c
                       ON d.car=c.car_num
                       WHERE d.first_name LIKE %s OR d.surname LIKE %s""", (f'%{input}%', f'%{input}%'))
        drivers = connection.fetchall()
        print(drivers)
        if drivers:
            # # Get runs data
            # connection.execute(
            #     "SELECT * FROM run WHERE dr_id = %s;", (driver[0],))
            # run_data = connection.fetchall()
            # print(run_data)

            # # Get a list of all the courses' information
            # connection.execute("SELECT * FROM course;")
            # courses = connection.fetchall()
            return render_template("search_results.html", drivers=drivers)
        else:
            message = f"Could't find '{input}'. Please check your input."
            return render_template("search_results.html", message=message)
    return render_template("admin_base.html")
