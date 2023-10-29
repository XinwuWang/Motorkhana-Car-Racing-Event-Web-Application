# 2023S2-BRMM-webapp

**Name: Xinwu Wang**  
**Student ID: 1154492**

[GitHub](https://github.com/XinwuWang/2023S2-BRMM-webapp)

- URL: https://github.com/XinwuWang/2023S2-BRMM-webapp

[Pythonanywhere](https://xinwuwang.pythonanywhere.com/)

- URL: https://xinwuwang.pythonanywhere.com/

## Web application structure

**Web Application Structure**

![alt text](https://github.com/XinwuWang/2023S2-BRMM-webapp/blob/main/readme_images/webapp%20srtucture.jpg "webapp structure")

My web application has totally 15 routes, 14 templates, 6 provided course images, and 4 background images from other sources. There are 6 routes and 6 templates for the public interface, while 9 routes and 8 templates for the admin interface.

The routes, templates, database, and static files interact with each other to realise all the functionalities required by COMP636 Motorkhana final assignment. Functions under different routes in the 'app.py' file use MySQL queries to fetch data from the database. Jinja templates are widely used to pass data between HTML templates and routes in the 'app.py' file.

Route '/' is the home page of the public interface, fetching 'driver_id', 'first_name', and 'surname' to insert into the dropdown box in navigation bar in the 'base.html'. 'base.html' uses the Jinja template to get data passed from the 'home' function under this route and display data to users. When users select a driver from the dropdown box, Jinja templates will pass 'driver_id' to the 'driver_run_detail(driver_id)' function under route '/driver/<driver_id>'. The '/driver/<driver_id>' route will then use this driver_id to retrieve this id's details and run data. After fetching related data from MySQL database, route '/driver/<driver_id>' will pass it to 'driver_detail.html' using Jinja template. 'driver_detail.html' will then display received data to the public. Besides, the 'home()'function under route '/' also calculates 'run_total' as long as users arrive at this page. Thus, users can view latest data when heading over to other routes.

Route '/listdrivers' retrieves data from MySQL database and passes it to the 'driverlist.html' template which displays the received data to users. If users click a driver's name on the 'driverlist.html' template, Jinja templates will pass this driver's ID to route '/driver/<driver_id>' which will trigger the 'driver_run_detail(driver_id)' function.

## Assumptions and design decisions

## Database questions

## Image sources

- [home_bg1.jpg](https://unsplash.com/photos/racing-black-and-green-sports-car--EXF9shcTO0)  
  URL: https://unsplash.com/photos/racing-black-and-green-sports-car--EXF9shcTO0

- [home_bg2.jpg](https://unsplash.com/photos/red-and-white-ferrari-f-1-on-road-xUOe6B84d5E)  
  URL: https://unsplash.com/photos/red-and-white-ferrari-f-1-on-road-xUOe6B84d5E

- [home_bg3.jpg](https://unsplash.com/photos/a-man-standing-next-to-a-blue-sports-car-L5dAzeHju9k)  
  URL: https://unsplash.com/photos/a-man-standing-next-to-a-blue-sports-car-L5dAzeHju9k

- [admin_bg.jpg](https://unsplash.com/photos/black-car-instrument-panel-cluster-sn5tCXz_0Rs)  
  URL: https://unsplash.com/photos/black-car-instrument-panel-cluster-sn5tCXz_0Rs
