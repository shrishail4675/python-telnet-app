import main
import sftp_connection
import atexit
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
scheduler = BackgroundScheduler()

if __name__ == '__main__':

    # Telnet Job → 13:00 to 13:23 (every minute)
    # scheduler.add_job(
    #     main.schedule_print,
    #     trigger='cron',
    #     hour=12,
    #     minute='0-10',
    #     id='telnet_job',
    #     replace_existing=True
    # )

    # File Check Job → 15:00 to 15:58 (every minute)
    # scheduler.add_job(
    #     main.check_file_uploads,
    #     trigger='cron',
    #     hour=12,
    #     minute='0-58',
    #     id='file_check_job',
    #     replace_existing=True
    # )

    # SFTP Check Job → Every minute
    scheduler.add_job(
        sftp_connection.check_all_sftp,
        trigger='cron',
        hour=12,
        minute='0-59',
        id='sftp_job',
        replace_existing=True
    )

    scheduler.start()
    print("Scheduler started...")

    atexit.register(lambda: scheduler.shutdown())

    app.run(host='0.0.0.0', port=5000, debug=False)