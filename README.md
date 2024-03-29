# transportation-events
- In this project, I created a python web-based API integration to query information from a MSSQL database and using Flask as web application framework. The goal is to learn about using Python and SQL as a way to display our data in a user-friendly environment for others to search through. 

## Running the Application

1. Database Configuration:
- Ensure you have a SQL Server database with the necessary tables for transportation events. Update the DRIVER_NAME, SERVER_NAME, and DATABASE_NAME variables in app.py with your database details.

2. Once data base is configurated, run application: 
   1. Install Flash and pypyodbc
      ```bash
       pip install Flask pypyodbc
      ```
   2. Run the flask application file (app.py)
      ```bash
       python app.py
      ```
   3. This will start the Flask development server. Open the the web browser and go to
      'http://127.0.0.1:5000/' to access the index page

3. Web Interface
- Open the provided URL to access the index page.

- Use the search boxes, buttons, or other components on the web page to perform the following actions:

      a. Search events by person ID:
       Enter a person ID and click the search button.
       View the displayed events sorted by time.
  ![Person ID](images/personID.png)

      b. Search events by link ID:
      Enter a link ID and click the search button.
      View the displayed events sorted by time.

  ![Person ID](images/linkID.png)
      
      c. Show link details:
      After searching events by link ID,
      click on a link to view details like freespeed, capacity, and modes.
  ![Person ID](images/linkIdOutput.png)
      
      d. Get events in a specific time range:
      Choose the time range (e.g., between 7:00 and 8:00 AM) and enter a link ID.
      Click the search button to view events within the specified time range for the given link.
  ![Person ID](images//Range.png)
