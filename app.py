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
        SELECT
            [Time],
            [Type],
            [Person],
            [Amount],
            [Purpose],
            [TransactionPartner],
            NULL AS [Link],
            NULL AS [X],
            NULL AS [Y],
            NULL AS [ActType]
        FROM
            [dbo].[PersonMoney]
        WHERE
            [Person] = ?

        UNION ALL

        SELECT
            [Time],
            [Type],
            [Person],
            NULL AS [Amount],
            NULL AS [Purpose],
            NULL AS [TransactionPartner],
            [Link],
            NULL AS [X],
            NULL AS [Y],
            [ActType]
        FROM
            [dbo].[ActEnd]
        WHERE
            [Person] = ?

        UNION ALL

        SELECT
            [Time],
            [Type],
            [Person],
            NULL AS [Amount],
            NULL AS [Purpose],
            NULL AS [TransactionPartner],
            [Link],
            [X],
            [Y],
            [ActType]
        FROM
            [dbo].[ActStart]
        WHERE
            [Person] = ?
            
        ORDER BY
            [Time]
    """

    cursor.execute(query, (person_id, person_id, person_id))
    results = cursor.fetchall()

    # Convert [Time] to hours, minutes, seconds
    results = [(seconds_to_hms(row[0]), *row[1:]) for row in results]

    return results

def search_events_by_link_id(link_id):
    cursor = conn.cursor()

    query = f"""

        SELECT
            [Time],
            [Type],
            [Person],
            NULL AS [Amount],
            NULL AS [Purpose],
            NULL AS [TransactionPartner],
            [Link],
            NULL AS [X],
            NULL AS [Y],
            [ActType]
        FROM
            [dbo].[ActEnd]
        WHERE
            [Link] = ?

        UNION ALL

        SELECT
            [Time],
            [Type],
            [Person],
            NULL AS [Amount],
            NULL AS [Purpose],
            NULL AS [TransactionPartner],
            [Link],
            [X],
            [Y],
            [ActType]
        FROM
            [dbo].[ActStart]
        WHERE
            [Link] = ?
            
        ORDER BY
            [Time]
    """

    cursor.execute(query, (link_id, link_id))
    results = cursor.fetchall()

    # Convert [Time] to hours, minutes, seconds
    results = [(seconds_to_hms(row[0]), *row[1:]) for row in results]

    return results

def search_events_by_time_range(link_id, start_time, end_time):
    cursor = conn.cursor()
    
    query = f"""

        SELECT
            [Time],
            [Type],
            [Person],
            NULL AS [Amount],
            NULL AS [Purpose],
            NULL AS [TransactionPartner],
            [Link],
            NULL AS [X],
            NULL AS [Y],
            [ActType]
        FROM
            [dbo].[ActEnd]
        WHERE
            [Link] = ?

        UNION ALL

        SELECT
            [Time],
            [Type],
            [Person],
            NULL AS [Amount],
            NULL AS [Purpose],
            NULL AS [TransactionPartner],
            [Link],
            [X],
            [Y],
            [ActType]
        FROM
            [dbo].[ActStart]
        WHERE
            [Link] = ? AND
            [Time] BETWEEN ? AND ?
            
        ORDER BY
            [Time]
    """

    # Convert start_time and end_time to seconds
    start_seconds = sum(x * int(t) for x, t in zip([3600, 60, 1], start_time.split(':')))
    end_seconds = sum(x * int(t) for x, t in zip([3600, 60, 1], end_time.split(':')))

    cursor.execute(query, (link_id, link_id, start_seconds, end_seconds))
    results = cursor.fetchall()

    # Convert [Time] to hours, minutes, seconds
    results = [(seconds_to_hms(row[0]), *row[1:]) for row in results]

    return results

if __name__ == '__main__':
    app.run(debug=True)
