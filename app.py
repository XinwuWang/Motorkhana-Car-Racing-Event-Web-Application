# COMP636 Motorkhana Event Assignment
# Name: Xinwu Wang
# Student ID: 1154492

from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import session
import re
from datetime import datetime, date
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


### Routes for public(driver) interfaces start here ###
# Public: homepage
@app.route("/")
def home():
    connection = getCursor()

    # ---If run this web app using the local mysql file, keep and run the code below ---
    # Add the run_total column to the database if the column does not exist
    check_column_exists_query = """SELECT COUNT(*)
    FROM information_schema.columns
    WHERE table_schema='motorkhana'
    AND table_name='run'
    AND column_name='run_total'"""
    check_column_exists = check_column_exists_query.format(
        "motorkhana", "run", "run_total")
    connection.execute(check_column_exists)
    if not connection.fetchone()[0] > 0:
        add_column = "ALTER TABLE run ADD run_total FLOAT;"
        connection.execute(add_column)
    # ---If run this web app on Pythonanywhere, comment out above code about checking the 'run_total' column, and run the following code. ---

    # If the run_total column exists, execute MySQL query to make sure the run total results of each run up to date
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
    return render_template("base.html", drivers_info=drivers_info)


# Public: driver list
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


# Public: course list
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


# Public: a driver's details and all run data
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

    return render_template("driver_detail.html",
                           driver_id=driver_id,
                           driver=driver,
                           runsList=runsList,
                           courses=courses,
                           drivers_info=drivers_info
                           )


# Public: display overall results
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

    # Store the overall resutls dictionary in the Flask session object that can be retrieved in the "graph" route later.
    session["sorted_overall"] = sorted_overall

    # Create the 'drivers_info' list so on this route users can access the dropdown box in the navigation bar.
    # Data of this list will be passed to the navigation bar.
    drivers_info = sorted([(driver[0], driver[1], driver[2])
                          for driver in driver_info], key=lambda x: (x[1], x[2]))

    return render_template("overall_results.html",
                           sorted_overall=sorted_overall,
                           drivers_info=drivers_info
                           )


# Public: display the top 5 drivers graph
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

    return render_template("top5graph.html",
                           name_list=bestDriverList,
                           value_list=resultsList,
                           drivers_info=drivers_info
                           )


### Admin routes start from here ###
# Admin: dashboard/homepage
@app.route("/admin")
def admin_home():
    # After admin adds a new driver/new junior driver with a caregiver/new junior driver without a caregiver,
    # the admin dashboard will display a success message.
    # Here get the message passed from 'add_driver()', 'add_dr_caregiver()', and 'add_junior_noCg()'
    success_add_message = request.args.get("success_add_message")
    return render_template("admin_base.html", success_add_message=success_add_message)


# Admin: view the junior driver list
@app.route("/admin/junior_list")
def junior_list():
    connection = getCursor()
    connection.execute(
        "SELECT driver_id, first_name, surname, date_of_birth, age, caregiver FROM driver")
    all_drivers = connection.fetchall()

    junior_drivers_unsorted = []
    for driver in all_drivers:  # Loop through 'all_drivers' to get drivers aged between 12 and 25
        if driver[4] and 12 <= driver[4] <= 25:
            if driver[4] <= 16:
                for drivers in all_drivers:  # Loop through 'all_drivers' again
                    # if caregiver_id matches driver_id,
                    # append the junior driver's and their caregiver's information as a tuple to the 'junior_drivers_unsorted' list.
                    if drivers[0] == driver[5]:
                        junior_drivers_unsorted.append(
                            (driver[0], driver[1], driver[2], driver[3], driver[4], drivers[1] + " " + drivers[2], drivers[0]))
            else:
                junior_drivers_unsorted.append(
                    (driver[0], driver[1], driver[2], driver[3], driver[4], None, None))
    junior_drivers = sorted(junior_drivers_unsorted,
                            key=lambda x: (x[4], x[2]), reverse=True)

    return render_template("admin_junior_list.html", junior_drivers=junior_drivers)


# Admin: search for a driver
@app.route("/admin/drivers", methods=["GET", "POST"])
def search():
    connection = getCursor()
    if request.method == "POST":
        input = request.form.get("search_query")
        connection.execute("""SELECT d.driver_id, d.first_name, d.surname, d.age, c.model, c.drive_class
                       FROM driver d
                       LEFT JOIN car c
                       ON d.car=c.car_num
                       WHERE d.first_name LIKE %s OR d.surname LIKE %s""", (f'%{input}%', f'%{input}%'))
        drivers_unsorted = connection.fetchall()
        drivers = sorted(drivers_unsorted, key=lambda x: (x[2], x[1]))
        if drivers:
            return render_template("admin_search_results.html", drivers=drivers)
        else:
            message = f"Sorry...could't find '{input}'. Please check your input. :("
            return render_template("admin_search_results.html", message=message)
    return render_template("admin_base.html")


# Admin: access a driver's details and all run data
@app.route("/admin/drivers/<int:driver_id>")
def driver_data(driver_id):
    connection = getCursor()

    # Get runs list
    connection.execute("SELECT * FROM run")
    runsList = connection.fetchall()

    # Select a driver's information and his/her all runs' details
    connection.execute("""SELECT d.driver_id, d.first_name, d.surname, c.model, c.drive_class, d.age
                       FROM driver d
                       LEFT JOIN car c
                       ON d.car=c.car_num
                       WHERE d.driver_id = %s""", (driver_id,))
    driver = connection.fetchone()

    # Get a list of all the courses' information
    connection.execute("SELECT * FROM course;")
    courses = connection.fetchall()

    # Get success_message from "update_run"
    success_message = request.args.get("success_message")

    return render_template("admin_driver_page.html",
                           driver_id=driver_id,
                           driver=driver,
                           runsList=runsList,
                           courses=courses,
                           success_message=success_message
                           )


# Admin: update a driver's run data
@app.route("/admin/update_run", methods=["GET", "POST"])
def update_run():
    connection = getCursor()
    if request.method == "POST":
        driver_id = request.form.get("driver_id")
        # Get the first item that is the course ID in the course input string
        course_name = request.form.get("course_id")[0]
        run_number = request.form.get("run_number")
        new_time = request.form.get("time_edit")
        cones_input = request.form.get("cones_edit")
        # Check if a valid number is entered for cones
        # If the cones input is empty, set default value to None
        new_cones = cones_input if cones_input else None
        wd_input = request.form.get("wd_edit")
        # Check if a valid number is entered for wd
        # If the wd input is empty, set default value to 0
        new_wd = wd_input if wd_input else 0
        run_total = float(new_time) + (float(new_cones)
                                       if new_cones else 0) * 5 + float(new_wd) * 10

        # Update run data in MySQL database
        update_data_query = "UPDATE run SET seconds=%s, cones=%s, wd=%s, run_total=%s WHERE dr_id=%s AND crs_id=%s AND run_num=%s"
        connection.execute(update_data_query, (new_time, new_cones,
                           new_wd, run_total, driver_id, course_name, run_number))

        success_message = "✓ Yay!! You have successfully updated run data."

        # Go back to the driver's info page after updating run data
        return redirect(url_for("driver_data", driver_id=driver_id, success_message=success_message))


# Admin: add a driver aged over 25 to the database
@app.route("/admin/add_driver", methods=["GET", "POST"])
def add_driver():
    connection = getCursor()
    # Get all cars' data
    connection.execute("SELECT * FROM car")
    cars = connection.fetchall()

    # If admin submits the form, get data he has entered.
    # Lower all the input first and then capitalise the 'first_name' and 'surname'
    if request.method == "POST":
        add_fname = request.form.get("add_fname").lower().capitalize()
        add_sname = request.form.get("add_sname").lower().capitalize()
        add_carinfo = request.form.get("add_carinfo")

        # There might be possibilities of two drivers having the same first name and surname,
        # therefore I chose not to check if admin enters a fullname that already exists in the database.
        # As long as each driver has a unique id number.
        # Insert the new driver's information into the 'driver' table
        # Generate a new id for the user using the 'lastrowid' property
        connection.execute(
            """INSERT INTO driver
            VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (connection.lastrowid, add_fname,
             add_sname, None, None, None, add_carinfo)
        )

        # Retrieve the new driver's id from the 'driver' table
        # which exists in the first position of the last tuple in the driver list
        connection.execute("SELECT * FROM driver")
        new_drId = connection.fetchall()[-1][0]

        # Create a 'course_ids' list and a 'course_nums' list and add 12 run rows for the new driver
        # Time and cones set to None, wd to 0, and run_total to None
        course_ids = ["A", "B", "C", "D", "E", "F"]
        run_nums = [1, 2]
        for crs_id in course_ids:
            for run_num in run_nums:
                connection.execute(
                    """INSERT INTO run
                    VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                    (new_drId, crs_id, run_num, None, None, 0, None)
                )

        # Pass a success message to 'admin_home' after admin adds a new driver
        success_add_message = f"Hooray!! The new driver '{add_fname} {add_sname}' has been successfully added!"
        return redirect(url_for("admin_home", success_add_message=success_add_message))
    return render_template("admin_add_driver.html", cars=cars)


# Admin: check a new junior driver's age befor adding to the database
@app.route("/admin/add_junior", methods=["GET", "POST"])
def add_junior_driver():
    connection = getCursor()
    # Get all cars' data
    connection.execute("SELECT * FROM car")
    cars = connection.fetchall()

    # Get all drivers who are eligible to be a caregiver
    # Drivers with no date_of_birth data are seen as eligible caregivers as only juniors are required to enter DOB data
    connection.execute("""SELECT driver_id, first_name, surname, date_of_birth 
                       FROM driver 
                       WHERE date_of_birth IS NULL""")
    caregivers_unsorted = connection.fetchall()
    # Sort caregivers by their surname
    caregivers = sorted(caregivers_unsorted, key=lambda x: (x[2], x[1]))

    if request.method == "POST":
        # If admin enters a date of birth on the 'admin_home' page, get 'date_of_birth' data
        add_dobirth = request.form.get("add_dobirth")

        # Convert the string 'add_dobirth' to a datetime format
        dobirth = datetime.strptime(add_dobirth, "%Y-%m-%d")

        # Calculate the age
        today = date.today()
        age = today.year - dobirth.year - \
            ((today.month, today.day) < (dobirth.month, dobirth.day))

        if 12 <= age <= 16:
            return render_template("admin_add_dr_caregiver.html", dobirth=add_dobirth, age=age, cars=cars, caregivers=caregivers)
        elif 16 < age <= 25:
            return render_template("admin_add_junior_driver.html", dobirth=add_dobirth, age=age, cars=cars)
        elif 25 < age:
            return redirect(url_for("add_driver"))
        else:
            error_message = f"Sorry. The driver aged {age} is too young and not eligible to register. :("
            return render_template("admin_error_page.html", error_message=error_message)


# Admin: add a new junior driver aged 12-16
@app.route("/admin/add_dr_caregiver", methods=["GET", "POST"])
def add_dr_caregiver():
    connection = getCursor()
    if request.method == "POST":
        add_fname = request.form.get("add_fname").lower().capitalize()
        add_sname = request.form.get("add_sname").lower().capitalize()
        add_carinfo = request.form.get("add_carinfo")
        add_dobirth = request.form.get("add_dobirth")
        add_age = request.form.get("add_age")
        add_caregiver = request.form.get("add_caregiver")

        # There might be possibilities of two drivers having the same first name and surname,
        # therefore I chose not to check if admin enters a fullname that already exists in the database.
        # As long as each driver has a unique id number.
        # Insert the new driver's information into the 'driver' table
        # Generate a new id for the user using the 'lastrowid' property
        connection.execute(
            """INSERT INTO driver
            VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (connection.lastrowid, add_fname,
             add_sname, add_dobirth, add_age, add_caregiver, add_carinfo)
        )

        # Retrieve the new driver's id from the 'driver' table
        # which exists in the first position of the last tuple in the driver list
        connection.execute("SELECT * FROM driver")
        new_drId = connection.fetchall()[-1][0]

        # Create a 'course_ids' list and a 'course_nums' list and add 12 run rows for the new driver
        # Time and cones set to None, wd to 0, and run_total to None
        course_ids = ["A", "B", "C", "D", "E", "F"]
        run_nums = [1, 2]
        for crs_id in course_ids:
            for run_num in run_nums:
                connection.execute(
                    """INSERT INTO run
                    VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                    (new_drId, crs_id, run_num, None, None, 0, None)
                )

        # Pass a success message to 'admin_home' after admin adds a new driver
        success_add_message = f"Hooray!! The new junior driver '{add_fname} {add_sname}' has been successfully added!"
        return redirect(url_for("admin_home", success_add_message=success_add_message))


# Admin: add a new junior driver aged older than 16 and younger than 25
@app.route("/addin/add_ju_no_cg", methods=["GET", "POST"])
def add_junior_noCg():
    if request.method == "POST":
        add_fname = request.form.get("add_fname").lower().capitalize()
        add_sname = request.form.get("add_sname").lower().capitalize()
        add_carinfo = request.form.get("add_carinfo")
        add_dobirth = request.form.get("add_dobirth")

        # There might be possibilities of two drivers having the same first name and surname,
        # therefore I chose not to check if admin enters a fullname that already exists in the database.
        # As long as each driver has a unique id number.
        # Insert the new driver's information into the 'driver' table
        # Generate a new id for the user using the 'lastrowid' property
        connection.execute(
            """INSERT INTO driver
            VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (connection.lastrowid, add_fname,
             add_sname, add_dobirth, None, None, add_carinfo)
        )

        # Retrieve the new driver's id from the 'driver' table
        # which exists in the first position of the last tuple in the driver list
        connection.execute("SELECT * FROM driver")
        new_drId = connection.fetchall()[-1][0]

        # Create a 'course_ids' list and a 'course_nums' list and add 12 run rows for the new driver
        # Time and cones set to None, wd to 0, and run_total to None
        course_ids = ["A", "B", "C", "D", "E", "F"]
        run_nums = [1, 2]
        for crs_id in course_ids:
            for run_num in run_nums:
                connection.execute(
                    """INSERT INTO run
                    VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                    (new_drId, crs_id, run_num, None, None, 0, None)
                )

        # Pass a success message to 'admin_home' after admin adds a new driver
        success_add_message = f"Hooray!! The new junior driver '{add_fname} {add_sname}' has been successfully added!"
        return redirect(url_for("admin_home", success_add_message=success_add_message))
