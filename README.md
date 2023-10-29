# 2023S2-BRMM-webapp

**Name: Xinwu Wang**  
**Student ID: 1154492**

- [GitHub](https://github.com/XinwuWang/2023S2-BRMM-webapp)  
  URL: https://github.com/XinwuWang/2023S2-BRMM-webapp

* [Pythonanywhere](https://xinwuwang.pythonanywhere.com/)  
  URL: https://xinwuwang.pythonanywhere.com/

## Web application structure

![alt text](https://github.com/XinwuWang/2023S2-BRMM-webapp/blob/main/readme_images/webapp_srtucture.jpg "webapp structure")

My web application has totally 15 routes, 14 templates, 6 provided course images, and 4 background images from other sources. There are 6 routes and 6 templates for the public interface, while 9 routes and 8 templates for the admin interface.

The routes, templates, database, and static files interact with each other to realise all the functionalities required by COMP636 Motorkhana final assignment. Functions under different routes in the 'app.py' file use MySQL queries to fetch data from the database. Jinja templates are widely used to pass data between HTML templates and routes in the 'app.py' file. HTML templates use [BootStrap](https://getbootstrap.com/) to display user friendly frontend interfaces. Course images and background images for the public interface and the admin interface in the 'static' folder are retrieved and displayed by related templates.

**Public Interface**  
Route '/' is the home page of the public interface, fetching 'driver_id', 'first_name', and 'surname' to insert into the dropdown box in navigation bar in the 'base.html'. 'base.html' uses Jinja templates to get data passed from the 'home()' function under this route and display data to users. When users select a driver from the dropdown box, Jinja templates will pass 'driver_id' to the 'driver_run_detail(driver_id)' function under route '/driver/<driver_id>'. The '/driver/<driver_id>' route will then use this driver_id to retrieve this id's details and run data. After fetching related data from MySQL database, route '/driver/<driver_id>' will pass it to 'driver_detail.html' using Jinja templates. 'driver_detail.html' will then display received data to the public. Besides, the 'home()'function under route '/' also calculates 'run_total' as long as users arrive at this page. Thus, users can view latest data when heading over to other routes. The 'base.html' template allows users to head to different routes by clicking buttons in the navigation bar. The routes include '/listdrivers', '/listcourse', '/driver/<int:driver_id>', '/overallresults', and '/admin'.

Route '/listdrivers' retrieves data from MySQL database and passes it to the 'driverlist.html' template which displays the received data to users. If users click a driver's name on the 'driverlist.html' template, Jinja templates will pass this driver's ID to route '/driver/<driver_id>' which will trigger the 'driver_run_detail(driver_id)' function.

Route '/listcourses' fetches course data from the database and passes it to the 'courselist.html' template which displays each course' information and image.

Route '/driver/<int:driver_id>' gets driver id collected from users' choices by 'base.html', 'driverlist.html', and 'overall_results.html' templates, uses this id in the database query to fetch a specific driver's details, and passes data to 'driver_detail.html' to display.

Route '/overall_results' fetches drivers' run data from the database and calculates the overall results that will be passed to 'overall_results.html' to display to users. The Flask_Session extension is used here to store and pass the 'overall_results' dictionary to route '/graph' for ranking the drivers.

Route '/graph' gets the 'overall_results' dictionary from '/overall_results' and selects the first five fast drivers, passing together with related drivers' data collected from the database to 'Top5graph.html' to display to users.

**Admin Interface**  
Route '/admin' is the home page/dashboard for the admin only. The admin can access this route by clicking a link on the public home page of route '/'. Route '/admin' interacts with the 'admin_base.html' template which displays the admin home page to the admin. 'admin_base.html' can get the admin's input about adding a new driver, adding a new junior driver, or searching for a driver via forms. The admin's responses will be captured as data passed to routes '/admin/drivers', '/admin/add_driver', and '/admin/add_junior'. Route '/admin' also gets messages passed from '/admin/add_driver', '/admin/add_dr_caregiver', and '/admin/add_ju_no_cg', and sends them back to 'admin_base.html' to display. Besides, the 'admin_base.html' template allows the admin to go to route '/admin/junior_list', and route '/' for the public home interface.

Route '/admin/junior_list' fetches junior drivers' information from the database, and passes it to the 'admin_junior_list.html' to display to the admin.

Route '/admin/drivers' takes the admin's input on the 'admin_base.html' page as the value of the database query and searches for the specific driver's information in the database. The search results will be passed from the database via '/admin/drivers' to the 'admin_search_results.html' template to display.

Route '/admin/drivers/<int:driver_id>' takes driver_id data collected by the 'admin_search_results.html' template to look for details about this driver id using MySQL queries in the database. The database will send data back to '/admin/drivers/<int:driver_id>' which will then pass the data to the 'admin_driver_page.html' to display.

Route '/admin/update_run' retrieves the update data from the form in the 'admin_driver_page.html' template, then using the database queries to pass data to the database. After updating data in the database, '/admin/update_run' sends a success message and redirects to '/admin/drivers/<int:driver_id>'. The latter route will display the success message.

Route '/admin/add_driver' fetches car information from the database, and gets the admin's choice about adding a non junior driver from the 'admin_base.html' template, directing the admin to the 'admin_add_driver.html' page to fill up a form for adding the driver. After the form is submitted, route '/admin/add_driver' captures data passed from 'admin_add_driver.html' and uses database queries to insert it into the database.

Route '/admin/add_junior' gets date of birth data from the modal containing a form that asks the date of birth for adding a new junior driver in the 'admin_base.html' template. Meanwhile, this route fetches data of cars and drivers who are eligible to be a caregiver from the database. Based on the date of birth collected, the 'add_junior_driver()' function under this route uses the 'datetime' module to calculate the age. Depending on different ages, this route passes different data and directs the admin to different templates. If the age is over 25, this route directs the admin to 'admin_add_driver.html' with invisibility of the date of birth, the age, and the 'select a caregiver' functionality. If between 16 and 25, the admin will go to 'admin_add_junior_driver.html' with no need to select a caregiver. If between 12 and 16, the admin is required to select a caregiver. If under 12, the admin goes to 'admin_error_page.html' and sees an error message.

Route '/admin/add_dr_caregiver' gets data passed by the form from the 'admin_add_dr_caregiver.html'. The new junior driver aged 12-16 will be able to access this form and be required to select a caregiver. After the form is submitted, the data will be passed to this route which will save it to the database.

Route '/admin/add_ju_no_cg' retrieves data passed by the form in the 'admin_add_junior_driver.html' template. New junior drivers aged 16-25 can access this form. No caregiver needs to be selected for submitting the form. After getting the data from the admin's input, this route uses the MySQL queries to save data to the database.

Successfully adding new drivers' details to the database under routes '/admin/add_driver', '/admin/add_dr_caregiver', and '/admin/add_ju_no_cg' will pass a success message to route '/admin' and display it in the 'admin_base.html' page.

## Assumptions and design decisions

## Database questions

- **SQL statement creating the car table and defining its three fields**

  - CREATE TABLE IF NOT EXISTS car
    (
    car_num INT PRIMARY KEY NOT NULL,
    model VARCHAR(20) NOT NULL,
    drive_class VARCHAR(3) NOT NULL
    );

- **SQL code setting up the relationship between the car and driver tables**

  - CREATE TABLE IF NOT EXISTS driver
    (
    driver_id INT auto_increment PRIMARY KEY NOT NULL,
    first_name VARCHAR(25) NOT NULL,
    surname VARCHAR(25) NOT NULL,
    date_of_birth DATE,
    age INT,
    caregiver INT,
    car INT NOT NULL,
    FOREIGN KEY (caregiver) REFERENCES driver(driver_id)
    ON UPDATE CASCADE,
    **FOREIGN KEY (car) REFERENCES car(car_num)**
    ON UPDATE CASCADE
    ON DELETE CASCADE
    );

- **3 lines of SQL code inserting the Mini and GR Yaris details into the car table**  
  One

- **SQL code setting a defaul value of 'RWD' for the driver_class field**  
  One

- **Reasons why drivers and the admin access different routes, and examples of problems of everyone using the same routes**  
  One

## Image sources

- [home_bg1.jpg](https://unsplash.com/photos/racing-black-and-green-sports-car--EXF9shcTO0)  
  URL: https://unsplash.com/photos/racing-black-and-green-sports-car--EXF9shcTO0

- [home_bg2.jpg](https://unsplash.com/photos/red-and-white-ferrari-f-1-on-road-xUOe6B84d5E)  
  URL: https://unsplash.com/photos/red-and-white-ferrari-f-1-on-road-xUOe6B84d5E

- [home_bg3.jpg](https://unsplash.com/photos/a-man-standing-next-to-a-blue-sports-car-L5dAzeHju9k)  
  URL: https://unsplash.com/photos/a-man-standing-next-to-a-blue-sports-car-L5dAzeHju9k

- [admin_bg.jpg](https://unsplash.com/photos/black-car-instrument-panel-cluster-sn5tCXz_0Rs)  
  URL: https://unsplash.com/photos/black-car-instrument-panel-cluster-sn5tCXz_0Rs
