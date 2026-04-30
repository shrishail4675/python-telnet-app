# db_check.py
import oracledb
from datetime import datetime
from twilio.rest import Client
import traceback


# 🔹 DB Connection
def get_connection():
    return oracledb.connect(
        user="your_user",
        password="your_password",
        dsn="localhost:1521/XEPDB1"
    )


# Fetch columns dynamically from Oracle DB
def get_table_columns(conn, table_name):
    cursor = conn.cursor()

    cursor.execute("""
        SELECT column_name
        FROM user_tab_columns
        WHERE table_name = :1
    """, [table_name.upper()])

    #Exclude unwanted columns here
    excluded_columns = ['SRNO']

    columns = [
        row[0].lower()
        for row in cursor.fetchall()
        if row[0] not in excluded_columns
    ]

    cursor.close()
    return columns

# Main Check Function
def check_data_updated():
    today = datetime.now().strftime("%d/%m/%Y")
    message = ""

    conn = None
    cursor = None

    try:
        # DB connection
        conn = get_connection()
        cursor = conn.cursor()

        #dynamically fetch columns (NO hardcoding)
        columns = get_table_columns(conn, "ABC")

        not_updated = []

        # Check each column
        for col in columns:
            try:
                query = f"SELECT COUNT(*) FROM ABC WHERE {col} LIKE :1"
                cursor.execute(query, [f"%{today}%"])
                count = cursor.fetchone()[0]

                if count == 0:
                    not_updated.append(col)

            except Exception:
                not_updated.append(f"{col} (ERROR)")

        # Build message
        if not_updated:
            message = f"""Daily Data Check ({today})

Issues found:
{chr(10).join(['- ' + col for col in not_updated])}
"""
        else:
            message = f"""Daily Data Check ({today})

All columns are updated successfully.
"""

    except Exception as e:
        # Any failure (DB or unexpected)
        message = f"""Daily Data Check ({today})

ERROR OCCURRED

Error:
{str(e)}

Trace:
{traceback.format_exc()}
"""

    finally:
        try:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        except:
            pass

        # OPTIONAL: send WhatsApp here
        # send_whatsapp(message)

    return message