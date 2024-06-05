import paho.mqtt.client as mqtt
from flask import Flask, render_template, request, redirect, url_for
import datetime
import pytz
import sqlite3

app = Flask(__name__)

DATABASE = 'users.db'
UZBEK_TZ = pytz.timezone('Asia/Tashkent')

def get_db():
    conn = sqlite3.connect(DATABASE)
    return conn

@app.route('/')
def index():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT users.id, users.uid, users.name, MAX(usage_log.usage_time) AS last_usage_time
        FROM users
        LEFT JOIN usage_log ON users.id = usage_log.user_id
        GROUP BY users.id, users.uid, users.name
    """)
    users = cur.fetchall()

    cur.execute("""
        SELECT users.name, usage_log.usage_time
        FROM usage_log
        JOIN users ON usage_log.user_id = users.id
        ORDER BY usage_log.usage_time DESC
        LIMIT 100
    """)
    usage_history = cur.fetchall()

    conn.close()

    # Convert usage times to Uzbek local time
    users = [(user[0], user[1], user[2], convert_to_uzbek_time(user[3])) for user in users]
    usage_history = [(log[0], convert_to_uzbek_time(log[1])) for log in usage_history]

    return render_template('index.html', users=users, usage_history=usage_history)

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        uid = request.form['uid']
        name = request.form['name']
        conn = get_db()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users (uid, name) VALUES (?, ?)", (uid, name))
            conn.commit()
        except Exception as e:
            print(f"Error adding user: {e}")
        finally:
            conn.close()
        return redirect(url_for('index'))
    return render_template('add_user.html')

@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
    cur.execute("DELETE FROM usage_log WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/trigger_relay', methods=['POST'])
def trigger_relay():
    client.publish("esp32/relay", "TRIGGER_RELAY")
    return redirect(url_for('index'))

def check_user(uid):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM users WHERE uid = ?", (uid,))
    user = cur.fetchone()
    conn.close()
    return user

def log_use(user_id):
    conn = get_db()
    cur = conn.cursor()
    now_utc = datetime.datetime.now(pytz.utc)
    now_uzbek = now_utc.astimezone(UZBEK_TZ)
    now_uzbek_str = now_uzbek.strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("INSERT INTO usage_log (user_id, usage_time) VALUES (?, ?)", (user_id, now_uzbek_str))
    conn.commit()
    conn.close()

def convert_to_uzbek_time(utc_time_str):
    if utc_time_str:
        utc_time = datetime.datetime.strptime(utc_time_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.utc)
        uzbek_time = utc_time.astimezone(UZBEK_TZ)
        return uzbek_time.strftime("%Y-%m-%d %H:%M:%S")
    return None

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("esp32/uid")

def on_message(client, userdata, msg):
    uid = msg.payload.decode()
    user = check_user(uid)
    if user:
        log_use(user[0])
        client.publish("esp32/relay", "TRIGGER_RELAY")
    else:
        print(f"Unauthorized UID: {uid}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# If the ESP32 connects to the broker running on the host machine, use the host's IP address
client.connect("mosquitto", 1883, 60)

client.loop_start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
