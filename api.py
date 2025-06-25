from fastapi import FastAPI, Form, Query, Body, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from typing import Optional
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import json, sqlite3, time, os, requests

app = FastAPI()
scheduler = BackgroundScheduler()
scheduler.start()

REMINDER_DB_FILE = "reminders.db"
LOA_DB_FILE = "loa.db"
IA_DATA_FILE = "ia_data.db"
TRAINING_DATA_FILE = "training_data.db"
CORRECT_API_KEY = "SecurePassword"


def trigger_reminder(user_id: int, reminder: str, job_id: str, created_time: int):
    data = {
        "variables": [
            {
                "name": "dm_user_id",
                "variable": "{dm_user_id}",
                "value": str(user_id)
            },
            {
                "name": "reminder",
                "variable": "{reminder}",
                "value": reminder
            },
            {
                "name": "created_time",
                "variable": "{time_variable}",
                "value": created_time
            }
        ]
    }
    headers = {
        "Authorization": "[REMOVED]",
        "Content-Type": "application/json"
    }

    response = requests.post("[REMOVED]", json=data,
                             headers=headers)

    print(
        f"Reminder triggered - userID: {user_id}, jobID: {job_id}, reminder: {reminder}\nStatus code: {response.status_code}")

    conn = sqlite3.connect(REMINDER_DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reminders WHERE job_id = ?", (job_id,))
    conn.commit()
    conn.close()


def trigger_loa(user_id: int, created_date: int, reason: str, type):
    data = {
        "variables": [
            {
                "name": "type",
                "variable": "{type}",
                "value": "loa started"
            },
            {
                "name": "created_date",
                "variable": "{created_date}",
                "value": created_date
            },
            {
                "name": "dm_user_id",
                "variable": "{dm_user_id}",
                "value": str(user_id)
            }
        ]
    }
    headers = {
        "Authorization": "[REMOVED]",
        "Content-Type": "application/json"
    }

    response = requests.post("[REMOVED]", json=data,
                             headers=headers)

    print(f"LOA Ended - userID: {user_id}, creation date: {created_date}\nStatus code: {response.status_code}")

    conn = sqlite3.connect(LOA_DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM loas WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def trigger_trigger_loa(user_id, reason, end_date, type_, end_hour_offset: int):
    data = {
        "variables": [
            {
                "name": "type",
                "variable": "{type}",
                "value": "loa accepted"
            },
            {
                "name": "reason",
                "variable": "{reason}",
                "value": reason
            },
            {
                "name": "end_date",
                "variable": "{end_date}",
                "value": end_date
            },
            {
                "name": "dm_user_id",
                "variable": "{dm_user_id}",
                "value": user_id
            }
        ]
    }
    headers = {
          "Authorization": "[REMOVED",
        "Content-Type": "application/json"
    }

    response = requests.post("[REMOVED]", json=data,
                             headers=headers)

    delay_seconds = seconds_from_now(end_date)
    end_time = datetime.now() + timedelta(seconds=delay_seconds, hours=end_hour_offset)
    unix_ts = int(end_time.timestamp())
    job_id = f"{unix_ts * 2}"

    scheduler.add_job(
        trigger_loa,
        'date',
        run_date=end_time,
        args=[user_id, reason, job_id, "loa"],
        id=job_id
    )

    conn = sqlite3.connect(LOA_DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM loas WHERE user_id = ?", (user_id,))
    cursor.execute('''
            INSERT INTO loas (job_id, user_id, reason, trigger_time)
            VALUES (?, ?, ?, ?)
        ''', (job_id, user_id, reason, int(end_time.timestamp())))
    conn.commit()
    conn.close()


def seconds_from_now(date_str):
    # Parse input date
    input_date = datetime.strptime(date_str, "%m/%d/%Y")
    now = datetime.now()

    # Calculate time difference
    delta = input_date - now
    seconds = int(delta.total_seconds())

    return seconds


def hour_offset(input_str):
    try:
        dt = datetime.strptime(input_str, "%I%p")
        return dt.hour + 4 if dt.hour != 0 else 4
    except ValueError:
        return "not good"


def get_remindme_duration(input_str):
    input_str = str(input_str)
    if not input_str[:-1].isdigit():
        return "ValueError"

    value = int(input_str[:-1])
    unit = input_str[-1].lower()

    if unit == "s":
        return value
    elif unit == "m":
        return value * 60
    elif unit == "h":
        return value * 3600
    elif unit == "d":
        return value * 86400
    else:
        return "ValueError"


def get_table_from_type(type_):
    if type_ == "igs":
        return "loas_igs"
    elif type_ == "ds":
        return "loas_ds"
    else:
        raise HTTPException(status_code=422, detail="Invalid type_")


@app.get("/")
def default():
    return JSONResponse(content={"message": "Success!"})


### *** ### *** ### *** ### *** ### *** ### *** ### *** ### *** ### *** ### *** ### *** ### *** ### ***

@app.get("/ia-logs")
def get_ia_data(
        USERNAME: str = Query(...),
        TYPE: str = Query(...)):
    try:
        conn = sqlite3.connect(IA_DATA_FILE)
        cursor = conn.cursor()

        if USERNAME and TYPE:
            cursor.execute('''
                SELECT * FROM entries WHERE USERNAME = ? AND TYPE = ?
            ''', (USERNAME, TYPE))

        rows = cursor.fetchall()
        conn.close()

        if rows:
            return rows, {"message": "Success!"}, {"Length": len(rows)}
        else:
            return JSONResponse(content={"message": "No matching entries found"}, status_code=404)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/ia-logs")
def post_ia_data(
        USERNAME: str = Body(...),
        TYPE: str = Body(...),
        CREATION_DATE: str = Body(...),
        END_DATE: str = Body(...),
        REASON: str = Body(...),
        CREATED_BY: str = Body(...),
        STRIKE_NUM: Optional[int] = Body(None),
        MESSAGE_ID: str = Body(...)
):
    try:
        conn = sqlite3.connect(IA_DATA_FILE)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO entries (USERNAME, TYPE, CREATION_DATE, END_DATE, REASON, CREATED_BY, STRIKE_NUM, MESSAGE_ID, STATUS)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (USERNAME, TYPE, CREATION_DATE, END_DATE, REASON, CREATED_BY, STRIKE_NUM, MESSAGE_ID, "Active"))

        conn.commit()
        conn.close()

        return JSONResponse(content={"message": "Data added successfully"})

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/ia-logs/edit")
def edit_ia_log_status(
        MESSAGE_ID: str = Body(...),
        STATUS: str = Body(...)
):
    try:
        conn = sqlite3.connect(IA_DATA_FILE)
        cursor = conn.cursor()

        # Check if the log with the given USERNAME and MESSAGE_ID exists
        cursor.execute("SELECT * FROM entries WHERE MESSAGE_ID = ?", (MESSAGE_ID,))
        log = cursor.fetchone()

        if not log:
            return JSONResponse(content={"message": "Log not found"}, status_code=404)

        # Update the log's STATUS field
        cursor.execute("UPDATE entries SET STATUS = ? WHERE MESSAGE_ID = ?", (STATUS, MESSAGE_ID))
        conn.commit()
        conn.close()

        return JSONResponse(content={"message": "Success"})

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/ia-logs/delete")  # Delete a log based on a user
def delete_ia_log(USERNAME: str = Query(...), api_key: str = Query(...)):
    if api_key != CORRECT_API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden: Invalid API Key")

    conn = sqlite3.connect(IA_DATA_FILE)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM entries WHERE USERNAME = ?", (USERNAME,))
    conn.commit()
    conn.close()

    return JSONResponse(content={"message": "Entry deleted."}, status_code=200)


@app.get("/ia-logs/list")
def list_ia_logs(USERNAME: str = Query(...)):
    # Initialize counters for each type
    warnings = strikes = suspensions = demotions = terminations = blacklists = retirements = 0

    conn = sqlite3.connect(IA_DATA_FILE)
    cursor = conn.cursor()

    # Query all logs for the specified USERNAME
    cursor.execute("SELECT TYPE FROM entries WHERE USERNAME = ?", (USERNAME,))
    rows = cursor.fetchall()
    conn.close()

    # Count each type
    for row in rows:
        log_type = row[0].lower()
        if log_type == "warning":
            warnings += 1
        elif log_type == "strike":
            strikes += 1
        elif log_type == "suspension":
            suspensions += 1
        elif log_type == "demotion":
            demotions += 1
        elif log_type == "termination":
            terminations += 1
        elif log_type == "blacklist":
            blacklists += 1
        elif log_type == "retirement":
            retirements += 1

    return {
        "USERNAME": USERNAME,
        "warnings": warnings,
        "strikes": strikes,
        "suspensions": suspensions,
        "demotions": demotions,
        "terminations": terminations,
        "blacklists": blacklists,
        "retirements": retirements
    }


@app.get("/ia-logs/download")
def download_ia(api_key: str = Query(...)):
    if api_key != CORRECT_API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden: Invalid API Key")

    return FileResponse(
        path=IA_DATA_FILE,
        media_type='application/octet-stream',
        filename=IA_DATA_FILE
    )


@app.get("/ia-logs/setup")
def setup_ia(api_key: str = Query(...)):
    if api_key != CORRECT_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")

    conn = sqlite3.connect(IA_DATA_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            USERNAME TEXT,
            TYPE TEXT,
            CREATION_DATE TEXT,
            END_DATE TEXT,
            REASON TEXT,
            CREATED_BY TEXT,
            STRIKE_NUM INTEGER,
            MESSAGE_ID TEXT,
            STATUS TEXT
        )
    ''')
    conn.commit()

    try:
        with open("saved_ia_logs.txt", "r") as f:
            data = json.load(f)

        for row in data.get("entries", []):
            if len(row) == 8:
                cursor.execute('''
                    INSERT INTO entries (USERNAME, TYPE, CREATION_DATE, END_DATE, REASON, CREATED_BY, STRIKE_NUM, MESSAGE_ID, STATUS)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', tuple(row))

        conn.commit()
        conn.close()
        return JSONResponse(content={"message": "Database initialized and data imported.", "data": data})
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Error loading data: {str(e)}")


### *** ### *** ### *** ### *** ### *** ### *** ### *** ### *** ### *** ### *** ### *** ### *** ### ***


@app.get("/training-logs")  # Get info based on user
def get_tm_data(USERNAME: str = Query(...)):
    try:
        conn = sqlite3.connect(TRAINING_DATA_FILE)
        cursor = conn.cursor()

        cursor.execute('''
                SELECT * FROM entries WHERE USERNAME = ?
            ''', (USERNAME,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "USERNAME": row[0],
                "HAS_TICKET_TM": row[1],
                "HAS_FAILED_TM": row[2],
                "HAS_TICKET_TDM": row[3],
                "HAS_FAILED_TDM": row[4]
            }
        else:
            return {
                "USERNAME": USERNAME,
                "HAS_TICKET_TM": False,
                "HAS_FAILED_TM": False,
                "HAS_TICKET_TDM": False,
                "HAS_FAILED_TDM": False
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.get("/training-logs/create")  # Create a log for a user
def create_training_log(USERNAME: str = Query(...)):
    conn = sqlite3.connect(TRAINING_DATA_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT 1 FROM entries WHERE USERNAME = ?", (USERNAME,))
    if cursor.fetchone():
        conn.close()
        return JSONResponse(content={"message": "Already exists"}, status_code=400)

    cursor.execute('''
        INSERT INTO entries (USERNAME, HAS_TICKET_TM, HAS_FAILED_TM, HAS_TICKET_TDM, HAS_FAILED_TDM)
        VALUES (?, ?, ?, ?, ?)
    ''', (USERNAME, "False", "False", "False", "False"))

    conn.commit()
    conn.close()
    return JSONResponse(content={"message": "Entry created successfully"})


@app.post("/training-logs/edit")
def edit_training_log(
        USERNAME: str = Body(...),
        HAS_TICKET_TM: Optional[str] = Body(None),
        HAS_FAILED_TM: Optional[str] = Body(None),
        HAS_TICKET_TDM: Optional[str] = Body(None),
        HAS_FAILED_TDM: Optional[str] = Body(None)
):
    conn = sqlite3.connect(TRAINING_DATA_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM entries WHERE USERNAME = ?", (USERNAME,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Username not found")

    updates = []
    values = []

    if HAS_TICKET_TM is not None:
        updates.append("HAS_TICKET_TM = ?")
        values.append(HAS_TICKET_TM)
    if HAS_FAILED_TM is not None:
        updates.append("HAS_FAILED_TM = ?")
        values.append(HAS_FAILED_TM)
    if HAS_TICKET_TDM is not None:
        updates.append("HAS_TICKET_TDM = ?")
        values.append(HAS_TICKET_TDM)
    if HAS_FAILED_TDM is not None:
        updates.append("HAS_FAILED_TDM = ?")
        values.append(HAS_FAILED_TDM)

    if updates:
        sql = f"UPDATE entries SET {', '.join(updates)} WHERE USERNAME = ?"
        values.append(USERNAME)
        cursor.execute(sql, tuple(values))
        conn.commit()

    conn.close()
    return JSONResponse(content={"message": "Entry updated successfully"})


@app.get("/training-logs/delete")  # Delete a log based on a user
def delete_training_log(USERNAME: str = Query(...)):
    conn = sqlite3.connect(TRAINING_DATA_FILE)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM entries WHERE USERNAME = ?", (USERNAME,))
    conn.commit()
    conn.close()

    return JSONResponse(content={"message": "Entry deleted."}, status_code=200)


@app.get("/training-logs/download")
def download_training(api_key: str = Query(...)):
    if api_key != CORRECT_API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden: Invalid API Key")

    return FileResponse(
        path=TRAINING_DATA_FILE,
        media_type='application/octet-stream',
        filename=TRAINING_DATA_FILE
    )


@app.get("/training-logs/setup")
def setup_training(api_key: str = Query(...)):
    if api_key != CORRECT_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")

    conn = sqlite3.connect(TRAINING_DATA_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            USERNAME TEXT,
            HAS_TICKET_TM TEXT,
            HAS_FAILED_TM TEXT,
            HAS_TICKET_TDM TEXT,
            HAS_FAILED_TDM TEXT
        )
    ''')
    conn.commit()

    try:
        with open("saved_training_logs.txt", "r") as f:
            data = json.load(f)

        for row in data.get("entries", []):
            if len(row) == 6:
                cursor.execute('''
                    INSERT INTO entries (USERNAME, HAS_TICKET_TM, HAS_FAILED_TM, HAS_TICKET_TDM, HAS_FAILED_TDM)
                    VALUES (?, ?, ?, ?, ?)
                ''', tuple(row))

        conn.commit()
        conn.close()
        return JSONResponse(content={"message": "Database initialized and data imported.", "data": data})
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Error loading data: {str(e)}")


### *** ### *** ### *** ### *** ### *** ### *** ### *** ### *** ### *** ### *** ### *** ### *** ### ***
@app.get("/reminders")
def view_reminders(user_id: int = Query(...)):
    conn = sqlite3.connect(REMINDER_DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT job_id, reminder, trigger_time FROM reminders WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        raise HTTPException(status_code=404, detail="No reminders found for this user.")

    reminders = []
    for job_id, reminder, trigger_time in rows:
        reminders.append({
            "job_id": job_id,
            "trigger_time": str(trigger_time),
            "reminder": reminder
        })

    return {"reminders": reminders}


@app.post("/reminders/add")
def add_reminder(
        user_id: int = Body(...),
        reminder=Body(...),
        timestamp=Body(...)
):
    delay_seconds = get_remindme_duration(timestamp)
    if delay_seconds == "ValueError":
        raise HTTPException(status_code=422, detail="Unable to parse duration")

    trigger_time = datetime.now() + timedelta(seconds=delay_seconds)
    unix_ts = int(trigger_time.timestamp())
    created_time = int(datetime.now().timestamp())
    job_id = f"{unix_ts * 2}"

    scheduler.add_job(
        trigger_reminder,
        'date',
        run_date=trigger_time,
        args=[user_id, reminder, job_id, created_time],
        id=job_id
    )

    conn = sqlite3.connect(REMINDER_DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
            INSERT INTO reminders (job_id, user_id, reminder, trigger_time)
            VALUES (?, ?, ?, ?)
        ''', (job_id, user_id, reminder, unix_ts))

    conn.commit()
    conn.close()

    return {
        "message": "Reminder scheduled",
        "trigger_time": unix_ts,
        "job_id": job_id,
        "user_id": user_id
    }


@app.post("/reminders/edit")
def edit_reminder(
        user_id: int = Body(...),
        job_id: int = Body(...),
        reminder: Optional[str] = Body(None),
        timestamp: Optional[str] = Body(None)
):
    if reminder is None and timestamp is None:
        return JSONResponse(content={"message": "Unable to detect edits"}, status_code=422)
    job_id = str(job_id)

    # Fetch the current reminder details
    conn = sqlite3.connect(REMINDER_DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reminders WHERE job_id = ?", (job_id,))
    row = cursor.fetchone()

    if not row or row[1] != user_id:
        conn.close()
        return JSONResponse(content={"message": "Reminder not found"}, status_code=404)

    # Use the current values
    current_reminder = row[2]
    current_trigger_time = int(row[3])
    created_time = scheduler.get_job(job_id).args[3]

    # Only update the fields you actually want to change
    if reminder is not None:
        current_reminder = reminder

    if timestamp is not None:
        delay_seconds = get_remindme_duration(timestamp)

        if delay_seconds == "ValueError" or delay_seconds > 315360000:
            conn.close()
            return JSONResponse(content={"message": "Unable to parse duration"}, status_code=422)

        current_trigger_time = int((datetime.now() + timedelta(seconds=delay_seconds)).timestamp())

    # Update the scheduler
    scheduler.remove_job(job_id)
    scheduler.add_job(
        trigger_reminder,
        'date',
        run_date=datetime.fromtimestamp(current_trigger_time),
        args=[user_id, current_reminder, job_id, created_time],
        id=job_id
    )

    # Save the updated values back to the database with ONLY NEW VALUES
    cursor.execute('''
                UPDATE reminders
                SET reminder = ?, trigger_time = ?
                WHERE job_id = ? AND user_id = ?
            ''', (current_reminder, current_trigger_time, job_id, user_id))

    conn.commit()
    conn.close()

    return JSONResponse(
        content={"message": "Reminder edited", "new_trigger_time": f"<t:{current_trigger_time}:R>",
                 "new_reminder": current_reminder})


@app.get("/reminders/delete")
def delete_reminder(job_id=Query(...)):
    try:
        scheduler.remove_job(job_id)
        conn = sqlite3.connect(REMINDER_DB_FILE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM reminders WHERE job_id = ?", (job_id,))
        conn.commit()
        conn.close()
        return {"message": "Reminder deleted"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"{e}")


@app.get("/reminders/setup")
def setup_reminders(api_key: str = Query(...)):
    if api_key != CORRECT_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")

    conn = sqlite3.connect(REMINDER_DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reminders (
            job_id TEXT,
            user_id TEXT,
            reminder TEXT,
            trigger_time TEXT
        )
    ''')
    conn.commit()

    try:
        with open("saved_reminders.txt", "r") as f:
            data = json.load(f)

        for row in data.get("reminders", []):
            if len(row) == 4:
                job_id, user_id, reminder, trigger_time_str = row["job_id"], row["user_id"], row["reminder"], row[
                    "trigger_time"]
                trigger_time = datetime.fromtimestamp(int(trigger_time_str))
                unix_ts = int(trigger_time.timestamp())
                created_time = unix_ts

                cursor.execute('''
                    INSERT INTO reminders (job_id, user_id, reminder, trigger_time)
                    VALUES (?, ?, ?, ?)
                ''', (job_id, user_id, reminder, unix_ts))

                scheduler.add_job(
                    trigger_reminder,
                    'date',
                    run_date=trigger_time,
                    args=[user_id, reminder, job_id, created_time],
                    id=job_id
                )

        conn.commit()
        conn.close()
        return JSONResponse(
            content={"message": "Database initialized and data imported to both DB and scheduler.", "data": data})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading data: {str(e)}")


@app.get("/reminders/download")
def download_reminders(api_key: str = Query(...)):
    if api_key != CORRECT_API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden: Invalid API Key")

    return FileResponse(
        path=REMINDER_DB_FILE,
        media_type='application/octet-stream',
        filename=REMINDER_DB_FILE
    )


########## ************ ########## ************ ########## ************ ########## ************ ########## ************ ########## ************
####                                                       DANGER                                                                          ####
########## ************ ########## ************ ########## ************ ########## ************ ########## ************ ########## ************

@app.get("/view-all-ia")
def view_all_ia(api_key: str = Query(...)):
    if api_key != CORRECT_API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden: Invalid API Key")

    try:
        # Connect to the database
        conn = sqlite3.connect(IA_DATA_FILE)
        cursor = conn.cursor()

        # Execute a query to retrieve all rows
        cursor.execute('SELECT * FROM entries')
        rows = cursor.fetchall()
        conn.close()

        # If there are entries, return them; otherwise, return a message
        if rows:
            return JSONResponse(content={"entries": rows})
        else:
            return JSONResponse(content={"message": "No entries found"}, status_code=404)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/delete-all-ia")
def delete_all_ia(api_key: str = Query(...)):
    if api_key != "special API key goes here":
        raise HTTPException(status_code=403, detail="Invalid API key")

    try:
        conn = sqlite3.connect(IA_DATA_FILE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM entries")
        conn.commit()
        conn.close()
        return {"message": "All entries deleted successfully."}
    except Exception as e:
        return {"error": str(e)}


@app.get("/view-all-training")
def view_all_training(api_key: str = Query(...)):
    if api_key != CORRECT_API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden: Invalid API Key")

    try:
        # Connect to the database
        conn = sqlite3.connect(TRAINING_DATA_FILE)
        cursor = conn.cursor()

        # Execute a query to retrieve all rows
        cursor.execute('SELECT * FROM entries')
        rows = cursor.fetchall()
        conn.close()

        # If there are entries, return them; otherwise, return a message
        if rows:
            return JSONResponse(content={"entries": rows})
        else:
            return JSONResponse(content={"message": "No entries found"}, status_code=404)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/delete-all-training")
def delete_all_training(api_key: str = Query(...)):
    if api_key != "special API key goes here":
        raise HTTPException(status_code=403, detail="Invalid API key")

    try:
        conn = sqlite3.connect(TRAINING_DATA_FILE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM entries")
        conn.commit()
        conn.close()
        return {"message": "All entries deleted successfully."}
    except Exception as e:
        return {"error": str(e)}


@app.get("/view-all-reminders")
def view_all_reminders(api_key: str = Query(...)):
    if api_key != CORRECT_API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden: Invalid API Key")

    conn = sqlite3.connect(REMINDER_DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT job_id, user_id, reminder, trigger_time FROM reminders")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return JSONResponse(content={"message": "No entries found"}, status_code=404)

    reminders = []
    for job_id, user_id, reminder, trigger_time in rows:
        reminders.append({
            "job_id": job_id,
            "user_id": user_id,
            "reminder": reminder,
            "trigger_time": str(trigger_time)
        })

    return {"reminders": reminders}


@app.get("/view-all-loa")
def view_all_loa(api_key: str = Query(...)):
    if api_key != CORRECT_API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden: Invalid API Key")

    conn = sqlite3.connect(LOA_DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT job_id, user_id, reason, trigger_time FROM loas_igs")
    rows_igs = cursor.fetchall()
    cursor.execute("SELECT job_id, user_id, reason, trigger_time FROM loas_ds")
    rows_ds = cursor.fetchall()
    conn.close()

    if not rows_igs or rows_ds:
        return JSONResponse(content={"message": "No entries found"}, status_code=404)

    loas_igs_list = []
    loas_ds_list = []

    for job_id, user_id, reason, trigger_time in rows_igs:
        try:
            if scheduler.get_job(job_id).args[4] is not None:
                loas_igs_list.append({
                    "job_id": job_id,
                    "user_id": user_id,
                    "reason": reason,
                    "type": "Future Start",
                    "end_date": scheduler.get_job(job_id).args[2],
                    "end_hour_offset": scheduler.get_job(job_id).args[4],
                    "trigger_time": str(trigger_time)
                })
        except Exception as e:
            loas_igs_list.append({
                "job_id": job_id,
                "user_id": user_id,
                "reason": reason,
                "type": "Active LOA",
                "trigger_time": str(trigger_time)
            })

    for job_id, user_id, reason, trigger_time in rows_ds:
        try:
            if scheduler.get_job(job_id).args[4] is not None:
                loas_ds_list.append({
                    "job_id": job_id,
                    "user_id": user_id,
                    "reason": reason,
                    "type": "Future Start",
                    "end_date": scheduler.get_job(job_id).args[2],
                    "end_hour_offset": scheduler.get_job(job_id).args[4],
                    "trigger_time": str(trigger_time)
                })
        except Exception as e:
            loas_ds_list.append({
                "job_id": job_id,
                "user_id": user_id,
                "reason": reason,
                "type": "Active LOA",
                "trigger_time": str(trigger_time)
            })

    return JSONResponse(content={"igs_loas": loas_igs_list, "ds_loas": loas_ds_list})


@app.get("/delete-all-loa")
def delete_all_loa(api_key: str = Query(...)):
    if api_key != "special API key goes here":
        raise HTTPException(status_code=403, detail="Invalid API key")

    try:
        conn = sqlite3.connect(LOA_DB_FILE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM loas_igs")
        cursor.execute("DELETE FROM loas_ds")
        conn.commit()
        conn.close()

        for job in scheduler.get_jobs():
            if "loa" in job.args[3]:
                scheduler.remove_job(job.id)

        return {"message": "All entries deleted successfully."}
    except Exception as e:
        return {"error": str(e)}


########## ************ ########## ************ ########## ************ ########## ************
##                                          TESTING                                          ##
########## ************ ########## ************ ########## ************ ########## ************


@app.get("/loa")
def view_loa(user_id=Query(...), type_=Query(...)):
    if type_ not in ["igs", "ds"]:
        return JSONResponse(content={"message": f"Incorrect type_ - {type_}"}, status_code=422)

    table = get_table_from_type(type_)
    user_jobs = []

    for job in scheduler.get_jobs():
        if int(job.args[0]) == int(user_id) and job.args[3] == f"loa-{type_}":
            unix_ts = int(job.next_run_time.timestamp()) if job.next_run_time else None
            try:
                if job.args[4] is not None:
                    user_jobs.append({
                        "job_id": job.id,
                        "trigger_time": unix_ts,
                        "reason": job.args[1],
                        "type": "Future",
                        "end_date": (int(datetime.now().timestamp()) + seconds_from_now(job.args[2])) + (
                                job.args[4] * 3600)
                    })
            except:
                user_jobs.append({
                    "job_id": job.id,
                    "trigger_time": unix_ts,
                    "reason": job.args[1],
                    "type": "Current"
                })

    if not user_jobs:
        raise HTTPException(status_code=404, detail=f"No LOAs were found")

    return {"results": user_jobs, "detail": "Success"}


@app.post("/loa/add")
def create_loa(
        user_id=Body(...),
        reason=Body(...),
        start_date=Body(...),
        end_date=Body(...),
        start_time: Optional[str] = Body(None),
        end_time=Body(...),
        type_=Body(...)
):
    if type_ not in ["igs", "ds"]:
        raise HTTPException(status_code=422, detail="Invalid type_")

    user_id = str(user_id)
    start_seconds = seconds_from_now(start_date)
    end_seconds = seconds_from_now(end_date)
    end_hour_offset = hour_offset(end_time)
    job_id = int(datetime.now().timestamp()) * 2
    table = get_table_from_type(type_)

    if start_time is None:
        start_hour_offset = hour_offset("9am")
    else:
        start_hour_offset = 0
    if start_hour_offset == "not good":
        return "start offset error"
    elif end_hour_offset == "not good":
        return "end offset error"

    if start_seconds < 0:  # Immediate LOA
        trigger_time = datetime.now() + timedelta(seconds=end_seconds, hours=end_hour_offset)

        scheduler.add_job(
            trigger_loa,
            'date',
            run_date=trigger_time,
            args=[user_id, reason, job_id, f"loa-{type_}"],
            id=str(job_id)
        )

        conn = sqlite3.connect(LOA_DB_FILE)
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {table} WHERE job_id = ?", (job_id,))
        cursor.execute(f'''
                    INSERT INTO {table} (job_id, user_id, reason, trigger_time)
                    VALUES (?, ?, ?, ?)
                ''', (job_id, user_id, reason, int(trigger_time.timestamp())))
        conn.commit()
        conn.close()

        return {
            "message": "LOA Created",
            "reason": reason,
            "end_date": int(trigger_time.timestamp()),
            "end_time": scheduler.get_job(f"{job_id}").next_run_time,
            "user_id": user_id
        }

    start_time = datetime.now() + timedelta(seconds=start_seconds, hours=start_hour_offset)
    start_unix = int(start_time.timestamp())

    conn = sqlite3.connect(LOA_DB_FILE)
    cursor = conn.cursor()
    cursor.execute(f'''
        INSERT INTO {table} (job_id, user_id, reason, trigger_time)
        VALUES (?, ?, ?, ?)
    ''', (job_id, user_id, reason, start_unix))
    conn.commit()
    conn.close()

    # Schedule the activation job
    scheduler.add_job(
        trigger_trigger_loa,
        'date',
        run_date=start_time,
        args=[user_id, reason, end_date, f"loa-{type_}", end_hour_offset],
        id=str(job_id)
    )
    return {
        "message": "LOA scheduled to activate later",
        "reason": reason,
        "start_date": start_unix,
        "end_date": int(start_time.timestamp()),
        "user_id": user_id
    }


@app.post("/loa/edit")
def edit_loa(
        user_id=Body(...),
        reason: Optional[str] = Body(None),
        end_date: Optional[str] = Body(None),
        start_date: Optional[str] = Body(None),
        start_time: Optional[str] = Body(None),
        type_=Body(...)
):
    table = get_table_from_type(type_)
    user_id = str(user_id)

    conn = sqlite3.connect(LOA_DB_FILE)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table} WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()

    if not row or row[1] != user_id:
        conn.close()
        return JSONResponse(content={"message": "LOA not found"}, status_code=404)

    job_id = row[0]
    old_reason = row[2]
    old_start_unix = int(row[3])
    job = scheduler.get_job(str(job_id))

    if not any([reason, end_date, start_date]):
        raise HTTPException(status_code=422, detail="Nothing to edit")

    args = job.args
    new_args = list(args)

    result = {"message": "LOA updated"}
    result["user_id"] = user_id
    result["job_id"] = job_id

    if reason:
        result["old_reason"] = old_reason
        result["new_reason"] = reason
        new_args[1] = reason
    else:
        reason = old_reason  # for later use in rescheduling

    if end_date:
        result["new_end_date"] = end_date

        if len(args) == 5:  # Future
            result["old_end_date"] = args[2]
            new_args[2] = end_date
        else:  # Active
            result["old_end_date"] = datetime.fromtimestamp(job.next_run_time.timestamp).strftime("%m/%d/%Y")
            new_trigger = datetime.fromtimestamp(seconds_from_now(end_date)) + timedelta(hours=13)
            scheduler.remove_job(str(job_id))
            scheduler.add_job(
                trigger_loa,
                'date',
                run_date=new_trigger,
                args=[user_id, reason, job_id, f"loa-{type_}"],
                id=str(job_id)
            )
            cursor.execute(f'''
                UPDATE {table}
                SET reason = ?, trigger_time = ?
                WHERE job_id = ? AND user_id = ?
            ''', (reason, int(new_trigger.timestamp()), job_id, user_id))
            conn.commit()
            conn.close()
            result["message"] = "LOA end_date updated (active LOA)"
            return result

    if start_date:
        if len(args) != 5:
            raise HTTPException(status_code=400, detail="Cannot edit start_date for active LOA")

        start_hour_offset = hour_offset("9am")
        start_seconds = seconds_from_now(start_date)
        new_start_time = datetime.now() + timedelta(seconds=start_seconds, hours=start_hour_offset)

        result["old_start_date"] = old_start_unix
        result["new_start_date"] = int(new_start_time.timestamp())

        new_args = [user_id, reason, new_args[2], f"loa-{type_}", new_args[4]]
        scheduler.remove_job(str(job_id))
        scheduler.add_job(
            trigger_trigger_loa,
            'date',
            run_date=new_start_time,
            args=new_args,
            id=str(job_id)
        )
        cursor.execute(f'''
            UPDATE {table}
            SET reason = ?, trigger_time = ?
            WHERE job_id = ? AND user_id = ?
        ''', (reason, int(new_start_time.timestamp()), job_id, user_id))
        conn.commit()
        conn.close()
        result["message"] = "LOA start_date updated (future LOA)"
        return result

    # Fallback for only reason update
    scheduler.remove_job(str(job_id))
    scheduler.add_job(
        job.func,
        'date',
        run_date=job.next_run_time,
        args=new_args,
        id=str(job_id)
    )

    cursor.execute(f'''
        UPDATE {table}
        SET reason = ?
        WHERE job_id = ? AND user_id = ?
    ''', (reason, job_id, user_id))

    conn.commit()
    conn.close()

    return result


@app.get("/loa/remove")
def loa_remove(user_id: int = Query(...), type_=Query(...)):
    try:
        table = get_table_from_type(type_)
        user_id = str(user_id)
        conn = sqlite3.connect(LOA_DB_FILE)
        cursor = conn.cursor()

        # Fetch the only LOA for this user
        cursor.execute(f"SELECT job_id FROM {table} WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            raise HTTPException(status_code=404, detail="LOA not found")

        job_id = row[0]

        # Remove from scheduler and DB
        scheduler.remove_job(job_id)
        cursor.execute(f"DELETE FROM {table} WHERE job_id = ?", (job_id,))
        conn.commit()
        conn.close()

        return {"message": "LOA deleted"}

    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/loa/start-now")
def start_loa(user_id=Query(...), type_=Query(...)):
    try:

        table = get_table_from_type(type_)
        user_id = str(user_id)
        conn = sqlite3.connect(LOA_DB_FILE)
        cursor = conn.cursor()

        # Fetch the only LOA for this user
        cursor.execute(f"SELECT job_id FROM {table} WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            raise HTTPException(status_code=404, detail="LOA not found")

        job_id = row[0]

        # Remove from scheduler & re-add
        job = scheduler.get_job(job_id)
        trigger_time = datetime.now() + timedelta(seconds=seconds_from_now(job.args[2]), hours=job.args[4])
        reason = job.args[1]
        scheduler.remove_job(job_id)

        scheduler.add_job(
            trigger_loa,
            'date',
            run_date=trigger_time,
            args=[user_id, reason, job_id, f"loa-{type_}"],
            id=str(job_id)
        )

        conn.commit()
        conn.close()

        return {"message": "LOA started"}

    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/loa/setup")
def setup_loa(api_key: str = Query(...)):
    if api_key != CORRECT_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")

    conn = sqlite3.connect(LOA_DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS loas_igs (
            job_id TEXT,
            user_id TEXT,
            reason TEXT,
            trigger_time TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS loas_ds (
            job_id TEXT,
            user_id TEXT,
            reason TEXT,
            trigger_time TEXT
        )
    ''')
    conn.commit()

    try:
        with open("saved_loas.txt", "r") as f:
            data = json.load(f)
        for row in data.get("loas", []):
            job_id, user_id, reason, trigger_time_str, type_ = row["job_id"], row["user_id"], row["reason"], row[
                "trigger_time"], row["type"]
            trigger_time = datetime.fromtimestamp(int(trigger_time_str))
            unix_ts = int(trigger_time.timestamp())
            table = get_table_from_type(type_)

            cursor.execute(f'''
                INSERT INTO {table} (job_id, user_id, reason, trigger_time)
                VALUES (?, ?, ?, ?)
            ''', (job_id, user_id, reason, unix_ts))

            if type_ == "Future Start":
                end_date, end_hour_offset = row["end_date"], row["end_hour_offset"]
                scheduler.add_job(
                    trigger_trigger_loa,
                    'date',
                    run_date=trigger_time,
                    args=[user_id, reason, end_date, f"loa-{type_}", end_hour_offset],
                    id=str(job_id)
                )
            elif type_ == "Active LOA":
                scheduler.add_job(
                    trigger_loa,
                    'date',
                    run_date=trigger_time,
                    args=[user_id, reason, job_id, f"loa-{type_}"],
                    id=str(job_id)
                )
        conn.commit()
        conn.close()
        return JSONResponse(
            content={"message": "Database initialized and data imported to both DB and scheduler.", "data": data})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading data: {str(e)}")


@app.get("/loa/download")
def download_loas(api_key: str = Query(...)):
    if api_key != CORRECT_API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden: Invalid API Key")

    return FileResponse(
        path=LOA_DB_FILE,
        media_type='application/octet-stream',
        filename=LOA_DB_FILE
    )


@app.get("/loa/jobs")
def smth():
    jobs = []
    for job in scheduler.get_jobs():
        if "loa" in job.args[3]:
            type_ = "LOA"
        else:
            type_ = "Reminder"
        jobs.append([job.next_run_time, job.args[1], type_])
    return jobs


@app.get("/ping-api")
def ping():
    return {"response": "Pinged!", "time": int(datetime.now().timestamp())}
