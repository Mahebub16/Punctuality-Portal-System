from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import csv
from io import StringIO
from flask import jsonify
from twilio.rest import Client  # Import Twilio library
account_sid = "YOUR_TWILIO_ACCOUNT_SID"
auth_token = "YOUR_TWILIO_AUTH_TOKEN"
twilio_number = "+13185363556"

app = Flask(__name__)
# # Drop existing table
# conn = sqlite3.connect('latecomers.db')
# cursor = conn.cursor()
# cursor.execute('DROP TABLE IF EXISTS latecomers')
# conn.commit()
# conn.close()



conn = sqlite3.connect('latecomers.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS latecomers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT NOT NULL,
        year TEXT,
        section TEXT,
        date TEXT DEFAULT (strftime('%d.%m.%Y', 'now', 'localtime')),
        time TEXT DEFAULT (strftime('%H:%M:%S', 'now', 'localtime'))   
    )
''')

conn.commit()
conn.close()


# Create or connect to the database for student phone numbers
conn_phone_numbers = sqlite3.connect('phone_numbers.db')
cursor_phone_numbers = conn_phone_numbers.cursor()

# Create the phone_numbers table if it doesn't exist
cursor_phone_numbers.execute('''
    CREATE TABLE IF NOT EXISTS phone_numbers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT NOT NULL,
        phone_number TEXT NOT NULL
    )
''')
conn_phone_numbers.commit()

# Close the connection to phone numbers database
conn_phone_numbers.close()


@app.route('/clear_database', methods=['POST'])
def clear_database():
    conn = sqlite3.connect('latecomers.db')
    cursor = conn.cursor()

    # Clear the entire 'latecomers' table
    cursor.execute('DELETE FROM latecomers')
    
    # Reset the auto-increment primary key sequence
    cursor.execute('DELETE FROM sqlite_sequence WHERE name="latecomers"')

    conn.commit()
    conn.close()

    return 'Database cleared successfully', 200

# Routes
@app.route('/')
def index():
    conn = sqlite3.connect('latecomers.db')
    cursor = conn.cursor()
    
    # Retrieve and display all latecomers
    cursor.execute('SELECT * FROM latecomers')
    latecomers = cursor.fetchall()
    
    conn.close()
    
    return render_template('index.html', latecomers=latecomers)


#######################################################
@app.route('/record_latecomer', methods=['POST'])
def record_latecomer():
    student_id = request.form['student_id'].upper()   # Convert to uppercase
    year = request.form['year']
    section = request.form['section'].upper()  # Convert to uppercase
    conn = sqlite3.connect('latecomers.db')
    cursor = conn.cursor()

    # Insert a new record for the current entry
    cursor.execute('INSERT INTO latecomers (student_id, year, section) VALUES (?, ?, ?)', (student_id, year, section))
    # cursor.execute('INSERT INTO latecomers (student_id, year, section, entry_count) VALUES (?, ?, ?, 1)', (student_id, year, section))
    entry_counts = cursor.fetchall()
    if len(entry_counts) >= 4:
        # If the student_id has been entered 7 times, update the entry_count for the existing entries
        updated_count = entry_counts[-1][0] + 1
        cursor.execute('UPDATE latecomers SET entry_count = ? WHERE UPPER(student_id) = ? AND year = ? AND UPPER(section) = ?', (updated_count, student_id, year, section))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))



#################################################################
# Add this route to fetch phone number
@app.route('/getPhoneNumber', methods=['GET'])
def get_phone_number():
    student_id = request.args.get('id')

    if student_id:
        conn = sqlite3.connect('phone_numbers.db')
        cursor = conn.cursor()

        cursor.execute('SELECT phone_number FROM phone_numbers WHERE student_id = ?', (student_id,))
        phone_number = cursor.fetchone()

        conn.close()

        if phone_number:
            return jsonify({'phone_number': phone_number[0]})
        else:
            return jsonify({'error': 'Phone number not found for student ID'}), 404
    else:
        return jsonify({'error': 'No student ID provided'}), 400
@app.route('/sendSMS', methods=['POST'])
def send_sms():
    data = request.json
    to = data.get('to')
    message = data.get('message')

    client = Client(account_sid, auth_token)

    try:
        message = client.messages.create(
            body=message,
            from_=twilio_number,
            to=to
        )
        return 'SMS sent successfully', 200
    except Exception as e:
        return str(e), 500

@app.route('/downloadData', methods=['POST'])
def download_data():
    from_date = request.json.get('from')
    to_date = request.json.get('to')

    # Connect to the SQLite database
    conn = sqlite3.connect('latecomers.db')
    cursor = conn.cursor()

    # Query the database for entries within the specified date range
    cursor.execute("SELECT student_id, year, section, date, time FROM latecomers WHERE date BETWEEN ? AND ?", (from_date, to_date))
    data = cursor.fetchall()
   
    # Convert data to CSV format
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Student ID', 'Year', 'Section', 'Date', 'Time'])
    writer.writerows(data)
    # Close the database connection
    conn.close()

    return output.getvalue(), 200, {'Content-Type': 'text/csv'}






if __name__ == '__main__':
    app.run(debug=True)




