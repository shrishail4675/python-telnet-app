import main
import sftp_connection
import atexit
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
scheduler = BackgroundScheduler()

if __name__ == '__main__':

    # Telnet Job at 05:00 to 05:30 (every 10 minutes)
    scheduler.add_job(
        main.schedule_print,
        trigger='cron',
        hour=5,
        minute='0-30/10',
        id='telnet_job',
        replace_existing=True
    )

    # File Check Job at 06:00 to 06:30 (every 10 minutes)
    scheduler.add_job(
        main.check_file_uploads,
        trigger='cron',
        hour=6,
        minute='0-30/10',
        id='file_check_job',
        replace_existing=True
    )

    # SFTP Check Job at 09:00 to 09:30 (every 10 minutes)
    scheduler.add_job(
        sftp_connection.check_all_sftp,
        trigger='cron',
        hour=9,
        minute='0-30/10',
        id='sftp_job',
        replace_existing=True
    )

    scheduler.start()
    print("Scheduler started...")

    atexit.register(lambda: scheduler.shutdown())

    app.run(host='0.0.0.0', port=5000, debug=False)