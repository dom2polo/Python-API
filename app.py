from flask import Flask, render_template, request
import pypyodbc as odbc
import datetime

DRIVER_NAME = 'SQL SERVER'
SERVER_NAME = 'dom2polo\\SQLEXPRESS'
DATABASE_NAME = 'transportationdb'

# Assuming Windows Authentication; modify the connection string accordingly for SQL Server authentication
connection_string = f"""
    DRIVER={{{DRIVER_NAME}}};
    SERVER={SERVER_NAME};
    DATABASE={DATABASE_NAME};
    Trusted_Connection=yes; 
"""

conn = odbc.connect(connection_string)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    search_option = request.form['search_option']
    person_value = request.form['person_value']
    link_value = request.form['link_value']
    search_value = request.form['search_value']

    if search_option == 'person_id':
        results = search_events_by_person_id(person_value)
    elif search_option == 'link_id':
        results = search_events_by_link_id(link_value)
    elif search_option == 'time_range':
        search_value = request.form['search_value']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        results = search_events_by_time_range(search_value, start_time, end_time)
    else:
        results = []

    return render_template('search_results.html', results=results)


def seconds_to_hms(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f'{int(hours)}:{int(minutes):02d}:{int(seconds):02d}'

def search_events_by_person_id(person_id):
    cursor = conn.cursor()

    query = f"""

        Select [Time], [Type], [Person], [Link], [ActType], NULL AS LegMode, NULL AS DvrpVehicle, NULL AS TaskType, NULL AS TaskIndex, NULL AS DvrpMode, NULL AS X, NULL AS Y, NULL AS Mode, NULL AS Request, NULL AS Vehicle, NULL AS Amount, NULL AS Purpose, NULL AS TransactionPartner, NULL AS Distance, NULL AS NetworkMode, NULL AS RelativePosition
        FROM [dbo].[ActEnd]
        WHERE [Person] = ?

        UNION ALL

        Select [Time], [Type], [Person], [Link], [ActType], NULL AS LegMode, NULL AS DvrpVehicle, NULL AS TaskType, NULL AS TaskIndex, NULL AS DvrpMode, [X], [Y], NULL AS Mode, NULL AS Request, NULL AS Vehicle, NULL AS Amount, NULL AS Purpose, NULL AS TransactionPartner, NULL AS Distance, NULL AS NetworkMode, NULL AS RelativePosition
        FROM [dbo].[ActStart]
        WHERE [Person] = ?

        UNION ALL

        Select [Time], [Type], [Person], [Link], NULL AS ActType, [LegMode], NULL AS DvrpVehicle, NULL AS TaskType, NULL AS TaskIndex, NULL AS DvrpMode, NULL AS X, NULL AS Y, NULL AS Mode, NULL AS Request, NULL AS Vehicle, NULL AS Amount, NULL AS Purpose, NULL AS TransactionPartner, NULL AS Distance, NULL AS NetworkMode, NULL AS RelativePosition
        FROM [dbo].[Arrival]
        WHERE [Person] = ?

        UNION ALL

        Select [Time], [Type], [Person], [Link], NULL AS ActType, [LegMode], NULL AS DvrpVehicle, NULL AS TaskType, NULL AS TaskIndex, NULL AS DvrpMode, NULL AS X, NULL AS Y, NULL AS Mode, NULL AS Request, NULL AS Vehicle, NULL AS Amount, NULL AS Purpose, NULL AS TransactionPartner, NULL AS Distance, NULL AS NetworkMode, NULL AS RelativePosition
        FROM [dbo].[Departure]
        WHERE [Person] = ?

        UNION ALL

        Select [Time], [Type], [Person], [Link], NULL AS ActType, NULL AS LegMode, [DvrpVehicle], [TaskType], [TaskIndex], [DvrpMode], NULL AS X, NULL AS Y, NULL AS Mode, NULL AS Request, NULL AS Vehicle, NULL AS Amount, NULL AS Purpose, NULL AS TransactionPartner, NULL AS Distance, NULL AS NetworkMode, NULL AS RelativePosition
        FROM [dbo].[DvrpTaskEnded]
        WHERE [Person] = ?

        UNION ALL

        Select [Time], [Type], [Person], [Link], NULL AS ActType, NULL AS LegMode, [DvrpVehicle], [TaskType], [TaskIndex], [DvrpMode], NULL AS X, NULL AS Y, NULL AS Mode, NULL AS Request, NULL AS Vehicle, NULL AS Amount, NULL AS Purpose, NULL AS TransactionPartner, NULL AS Distance, NULL AS NetworkMode, NULL AS RelativePosition
        FROM [dbo].[DvrpTaskStarted]
        WHERE [Person] = ?


        UNION ALL

        Select [Time], [Type], [Person], NULL AS Link,  NULL AS ActType, NULL AS LegMode, NULL AS DvrpVehicle, NULL AS TaskType, NULL AS TaskIndex, NULL AS DvrpMode, NULL AS X, NULL AS Y, [Mode], [Request], [Vehicle], NULL AS Amount, NULL AS Purpose, NULL AS TransactionPartner, NULL AS Distance, NULL AS NetworkMode, NULL AS RelativePosition
        FROM [dbo].[PassengerDroppedOff]
        WHERE [Person] = ?

        UNION ALL

        Select [Time], [Type], [Person], NULL AS Link,  NULL AS ActType, NULL AS LegMode, NULL AS DvrpVehicle, NULL AS TaskType, NULL AS TaskIndex, NULL AS DvrpMode, NULL AS X, NULL AS Y, [Mode], [Request], [Vehicle], NULL AS Amount, NULL AS Purpose, NULL AS TransactionPartner, NULL AS Distance, NULL AS NetworkMode, NULL AS RelativePosition
        FROM [dbo].[PassengerPickedUp]
        WHERE [Person] = ?

        UNION ALL

        Select [Time], [Type], [Person], NULL AS Link,  NULL AS ActType, NULL AS LegMode, NULL AS DvrpVehicle, NULL AS TaskType, NULL AS TaskIndex, NULL AS DvrpMode, NULL AS X, NULL AS Y, NULL AS Mode, NULL AS Request, [Vehicle], NULL AS Amount, NULL AS Purpose, NULL AS TransactionPartner, NULL AS Distance, NULL AS NetworkMode, NULL AS RelativePosition
        FROM [dbo].[PersonEntersVehicle]
        WHERE [Person] = ?

        UNION ALL

        Select [Time], [Type], [Person], NULL AS Link,  NULL AS ActType, NULL AS LegMode, NULL AS DvrpVehicle, NULL AS TaskType, NULL AS TaskIndex, NULL AS DvrpMode, NULL AS X, NULL AS Y, NULL AS Mode, NULL AS Request, [Vehicle], NULL AS Amount, NULL AS Purpose, NULL AS TransactionPartner, NULL AS Distance, NULL AS NetworkMode, NULL AS RelativePosition
        FROM [dbo].[PersonLeavesVehicle]
        WHERE [Person] = ?

        UNION ALL

        Select [Time], [Type], [Person], NULL AS Link, NULL AS ActType, NULL AS LegMode, NULL AS DvrpVehicle, NULL AS TaskType, NULL AS TaskIndex, NULL AS DvrpMode, NULL AS X, NULL AS Y, NULL AS Mode, NULL AS Request, NULL AS Vehicle, [Amount], [Purpose], [TransactionPartner], NULL AS Distance, NULL AS NetworkMode, NULL AS RelativePosition
        FROM [dbo].[PersonMoney]
        WHERE [Person] = ?

        UNION ALL

        Select [Time], [Type], [Person], NULL AS Link, NULL AS ActType, NULL AS LegMode, NULL AS DvrpVehicle, NULL AS TaskType, NULL AS TaskIndex, NULL AS DvrpMode, NULL AS X, NULL AS Y, [Mode], NULL AS Request, NULL AS Vehicle, NULL AS Amount, NULL AS Purpose, NULL AS TransactionPartner, [Distance], NULL AS NetworkMode, NULL AS RelativePosition
        FROM [dbo].[Travelled]
        WHERE [Person] = ?

        UNION ALL

        Select [Time], [Type], [Person], [Link], NULL AS ActType, NULL AS LegMode, NULL AS DvrpVehicle, NULL AS TaskType, NULL AS TaskIndex, NULL AS DvrpMode, NULL AS X, NULL AS Y, NULL AS Mode, NULL AS Request, [Vehicle], NULL AS Amount, NULL AS Purpose, NULL AS TransactionPartner, NULL AS Distance, [NetworkMode], [RelativePosition]
        FROM [dbo].[VehicleEntersTraffic]
        WHERE [Person] = ?

        UNION ALL

        Select [Time], [Type], [Person], [Link],  NULL AS ActType, NULL AS LegMode, NULL AS DvrpVehicle, NULL AS TaskType, NULL AS TaskIndex, NULL AS DvrpMode, NULL AS X, NULL AS Y, NULL AS Mode, NULL AS Request, [Vehicle], NULL AS Amount, NULL AS Purpose, NULL AS TransactionPartner, NULL AS Distance, [NetworkMode], [RelativePosition]
        FROM [dbo].[VehicleLeavesTraffic]
        WHERE [Person] = ?

        ORDER BY [Time];

    """

    # 10 parameters supplied 
    parameters = (person_id,) * 14

    cursor.execute(query, parameters)
    results = cursor.fetchall()

    # Close the cursor after fetching results
    cursor.close()

    # Convert [Time] to hours, minutes, seconds
    results = [(seconds_to_hms(row[0]), *row[1:]) for row in results]

    return results

def search_events_by_link_id(link_id):
    cursor = conn.cursor()

    query = f"""

        Select [Time], [Type], [Person], [Link], [ActType], NULL AS LegMode, NULL AS DvrpVehicle, NULL AS TaskType, NULL AS TaskIndex, NULL AS DvrpMode, NULL AS X, NULL AS Y, NULL AS Mode, NULL AS Request, NULL AS Vehicle, NULL AS Amount, NULL AS Purpose, NULL AS TransactionPartner, NULL AS Distance, NULL AS NetworkMode, NULL AS RelativePosition
        FROM [dbo].[ActEnd]
        WHERE [Link] = ?

        UNION ALL

        Select [Time], [Type], [Person], [Link], [ActType], NULL AS LegMode, NULL AS DvrpVehicle, NULL AS TaskType, NULL AS TaskIndex, NULL AS DvrpMode, [X], [Y], NULL AS Mode, NULL AS Request, NULL AS Vehicle, NULL AS Amount, NULL AS Purpose, NULL AS TransactionPartner, NULL AS Distance, NULL AS NetworkMode, NULL AS RelativePosition
        FROM [dbo].[ActStart]
        WHERE [Link] = ?

        UNION ALL

        Select [Time], [Type], [Person], [Link], NULL AS ActType, [LegMode], NULL AS DvrpVehicle, NULL AS TaskType, NULL AS TaskIndex, NULL AS DvrpMode, NULL AS X, NULL AS Y, NULL AS Mode, NULL AS Request, NULL AS Vehicle, NULL AS Amount, NULL AS Purpose, NULL AS TransactionPartner, NULL AS Distance, NULL AS NetworkMode, NULL AS RelativePosition
        FROM [dbo].[Arrival]
        WHERE [Link] = ?

        UNION ALL

        Select [Time], [Type], [Person], [Link], NULL AS ActType, [LegMode], NULL AS DvrpVehicle, NULL AS TaskType, NULL AS TaskIndex, NULL AS DvrpMode, NULL AS X, NULL AS Y, NULL AS Mode, NULL AS Request, NULL AS Vehicle, NULL AS Amount, NULL AS Purpose, NULL AS TransactionPartner, NULL AS Distance, NULL AS NetworkMode, NULL AS RelativePosition
        FROM [dbo].[Departure]
        WHERE [Link] = ?

        UNION ALL

        Select [Time], [Type], [Person], [Link], NULL AS ActType, NULL AS LegMode, [DvrpVehicle], [TaskType], [TaskIndex], [DvrpMode], NULL AS X, NULL AS Y, NULL AS Mode, NULL AS Request, NULL AS Vehicle, NULL AS Amount, NULL AS Purpose, NULL AS TransactionPartner, NULL AS Distance, NULL AS NetworkMode, NULL AS RelativePosition
        FROM [dbo].[DvrpTaskEnded]
        WHERE [Link] = ?

        UNION ALL

        Select [Time], [Type], [Person], [Link], NULL AS ActType, NULL AS LegMode, [DvrpVehicle], [TaskType], [TaskIndex], [DvrpMode], NULL AS X, NULL AS Y, NULL AS Mode, NULL AS Request, NULL AS Vehicle, NULL AS Amount, NULL AS Purpose, NULL AS TransactionPartner, NULL AS Distance, NULL AS NetworkMode, NULL AS RelativePosition
        FROM [dbo].[DvrpTaskStarted]
        WHERE [Link] = ?

        UNION ALL

        Select [Time], [Type], NULL AS Person, [Link],  NULL AS ActType, NULL AS LegMode, NULL AS DvrpVehicle, NULL AS TaskType, NULL AS TaskIndex, NULL AS DvrpMode, NULL AS X, NULL AS Y, NULL AS Mode, NULL AS Request, [Vehicle], NULL AS Amount, NULL AS Purpose, NULL AS TransactionPartner, NULL AS Distance, NULL AS NetworkMode, NULL AS RelativePosition
        FROM [dbo].[EnteredLink]
        WHERE [Link] = ?

        UNION ALL

        Select [Time], [Type], NULL AS Person, [Link],  NULL AS ActType, NULL AS LegMode, NULL AS DvrpVehicle, NULL AS TaskType, NULL AS TaskIndex, NULL AS DvrpMode, NULL AS X, NULL AS Y, NULL AS Mode, NULL AS Request, [Vehicle], NULL AS Amount, NULL AS Purpose, NULL AS TransactionPartner, NULL AS Distance, NULL AS NetworkMode, NULL AS RelativePosition
        FROM [dbo].[LeftLink]
        WHERE [Link] = ?

        UNION ALL

        Select [Time], [Type], [Person], [Link], NULL AS ActType, NULL AS LegMode, NULL AS DvrpVehicle, NULL AS TaskType, NULL AS TaskIndex, NULL AS DvrpMode, NULL AS X, NULL AS Y, NULL AS Mode, NULL AS Request, [Vehicle], NULL AS Amount, NULL AS Purpose, NULL AS TransactionPartner, NULL AS Distance, [NetworkMode], [RelativePosition]
        FROM [dbo].[VehicleEntersTraffic]
        WHERE [Link] = ?

        UNION ALL

        Select [Time], [Type], [Person], [Link], NULL AS ActType, NULL AS LegMode, NULL AS DvrpVehicle, NULL AS TaskType, NULL AS TaskIndex, NULL AS DvrpMode, NULL AS X, NULL AS Y, NULL AS Mode, NULL AS Request, [Vehicle], NULL AS Amount, NULL AS Purpose, NULL AS TransactionPartner, NULL AS Distance, [NetworkMode], [RelativePosition]
        FROM [dbo].[VehicleLeavesTraffic]
        WHERE [Link] = ?

        ORDER BY [Time];
    """

    # 10 parameters supplied 
    parameters = (link_id,) * 10

    cursor.execute(query, parameters)
    results = cursor.fetchall()

    # Close the cursor after fetching results
    cursor.close()


    # Convert [Time] to hours, minutes, seconds
    results = [(seconds_to_hms(row[0]), *row[1:]) for row in results]

    return results

def search_events_by_time_range(search_value, start_time, end_time):
    cursor = conn.cursor()
    
    query = f"""

        Select [Time], [Type], [Person], [Link], [ActType], NULL AS LegMode, NULL AS DvrpVehicle, NULL AS TaskType, NULL AS TaskIndex, NULL AS DvrpMode, NULL AS X, NULL AS Y, NULL AS Mode, NULL AS Request, NULL AS Vehicle, NULL AS Amount, NULL AS Purpose, NULL AS TransactionPartner, NULL AS Distance, NULL AS NetworkMode, NULL AS RelativePosition
        FROM [dbo].[ActEnd]
        WHERE 
            [Link] = ? AND 
            [Time] BETWEEN ? AND ?

        UNION ALL

        Select [Time], [Type], [Person], [Link], [ActType], NULL AS LegMode, NULL AS DvrpVehicle, NULL AS TaskType, NULL AS TaskIndex, NULL AS DvrpMode, [X], [Y], NULL AS Mode, NULL AS Request, NULL AS Vehicle, NULL AS Amount, NULL AS Purpose, NULL AS TransactionPartner, NULL AS Distance, NULL AS NetworkMode, NULL AS RelativePosition
        FROM [dbo].[ActStart]
        WHERE 
            [Link] = ? AND 
            [Time] BETWEEN ? AND ?

        UNION ALL

        Select [Time], [Type], [Person], [Link], NULL AS ActType, [LegMode], NULL AS DvrpVehicle, NULL AS TaskType, NULL AS TaskIndex, NULL AS DvrpMode, NULL AS X, NULL AS Y, NULL AS Mode, NULL AS Request, NULL AS Vehicle, NULL AS Amount, NULL AS Purpose, NULL AS TransactionPartner, NULL AS Distance, NULL AS NetworkMode, NULL AS RelativePosition
        FROM [dbo].[Arrival]
        WHERE 
            [Link] = ? AND 
            [Time] BETWEEN ? AND ?

        UNION ALL

        Select [Time], [Type], [Person], [Link], NULL AS ActType, [LegMode], NULL AS DvrpVehicle, NULL AS TaskType, NULL AS TaskIndex, NULL AS DvrpMode, NULL AS X, NULL AS Y, NULL AS Mode, NULL AS Request, NULL AS Vehicle, NULL AS Amount, NULL AS Purpose, NULL AS TransactionPartner, NULL AS Distance, NULL AS NetworkMode, NULL AS RelativePosition
        FROM [dbo].[Departure]
        WHERE 
            [Link] = ? AND 
            [Time] BETWEEN ? AND ?

        UNION ALL

        Select [Time], [Type], [Person], [Link], NULL AS ActType, NULL AS LegMode, [DvrpVehicle], [TaskType], [TaskIndex], [DvrpMode], NULL AS X, NULL AS Y, NULL AS Mode, NULL AS Request, NULL AS Vehicle, NULL AS Amount, NULL AS Purpose, NULL AS TransactionPartner, NULL AS Distance, NULL AS NetworkMode, NULL AS RelativePosition
        FROM [dbo].[DvrpTaskEnded]
        WHERE 
            [Link] = ? AND 
            [Time] BETWEEN ? AND ?

        UNION ALL

        Select [Time], [Type], [Person], [Link], NULL AS ActType, NULL AS LegMode, [DvrpVehicle], [TaskType], [TaskIndex], [DvrpMode], NULL AS X, NULL AS Y, NULL AS Mode, NULL AS Request, NULL AS Vehicle, NULL AS Amount, NULL AS Purpose, NULL AS TransactionPartner, NULL AS Distance, NULL AS NetworkMode, NULL AS RelativePosition
        FROM [dbo].[DvrpTaskStarted]
        WHERE 
            [Link] = ? AND 
            [Time] BETWEEN ? AND ?

        UNION ALL

        Select [Time], [Type], NULL AS Person, [Link],  NULL AS ActType, NULL AS LegMode, NULL AS DvrpVehicle, NULL AS TaskType, NULL AS TaskIndex, NULL AS DvrpMode, NULL AS X, NULL AS Y, NULL AS Mode, NULL AS Request, [Vehicle], NULL AS Amount, NULL AS Purpose, NULL AS TransactionPartner, NULL AS Distance, NULL AS NetworkMode, NULL AS RelativePosition
        FROM [dbo].[EnteredLink]
        WHERE 
            [Link] = ? AND 
            [Time] BETWEEN ? AND ?

        UNION ALL

        Select [Time], [Type], NULL AS Person, [Link],  NULL AS ActType, NULL AS LegMode, NULL AS DvrpVehicle, NULL AS TaskType, NULL AS TaskIndex, NULL AS DvrpMode, NULL AS X, NULL AS Y, NULL AS Mode, NULL AS Request, [Vehicle], NULL AS Amount, NULL AS Purpose, NULL AS TransactionPartner, NULL AS Distance, NULL AS NetworkMode, NULL AS RelativePosition
        FROM [dbo].[LeftLink]
        WHERE 
            [Link] = ? AND 
            [Time] BETWEEN ? AND ?

        UNION ALL

        Select [Time], [Type], [Person], [Link], NULL AS ActType, NULL AS LegMode, NULL AS DvrpVehicle, NULL AS TaskType, NULL AS TaskIndex, NULL AS DvrpMode, NULL AS X, NULL AS Y, NULL AS Mode, NULL AS Request, [Vehicle], NULL AS Amount, NULL AS Purpose, NULL AS TransactionPartner, NULL AS Distance, [NetworkMode], [RelativePosition]
        FROM [dbo].[VehicleEntersTraffic]
        WHERE 
            [Link] = ? AND 
            [Time] BETWEEN ? AND ?

        UNION ALL

        Select [Time], [Type], [Person], [Link], NULL AS ActType, NULL AS LegMode, NULL AS DvrpVehicle, NULL AS TaskType, NULL AS TaskIndex, NULL AS DvrpMode, NULL AS X, NULL AS Y, NULL AS Mode, NULL AS Request, [Vehicle], NULL AS Amount, NULL AS Purpose, NULL AS TransactionPartner, NULL AS Distance, [NetworkMode], [RelativePosition]
        FROM [dbo].[VehicleLeavesTraffic]
        WHERE 
            [Link] = ? AND 
            [Time] BETWEEN ? AND ?

        ORDER BY 
            [Time]
    """

    # Convert start_time and end_time to seconds
    start_seconds = sum(x * int(t) for x, t in zip([3600, 60, 1], start_time.split(':')))
    end_seconds = sum(x * int(t) for x, t in zip([3600, 60, 1], end_time.split(':')))

    # 10 parameters supplied 
    parameters = (search_value, start_seconds, end_seconds,) * 10

    cursor.execute(query, parameters)
    results = cursor.fetchall()

    # Close the cursor after fetching results
    cursor.close()

    # Convert [Time] to hours, minutes, seconds
    results = [(seconds_to_hms(row[0]), *row[1:]) for row in results]

    return results

if __name__ == '__main__':
    app.run(debug=True)
