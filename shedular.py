import bse_sftp_markrt_hrs
import db_check
import main
import nse_sftp_morning
import nse_sftp_market_hrs
import atexit
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

scheduler = BackgroundScheduler(
    job_defaults={
        'coalesce': True,
        'max_instances': 1
    }
)


def safe_job(func):
    def wrapper():
        try:
            print(f"Running job: {func.__name__}")
            func()
            print(f"Completed job: {func.__name__}")
        except Exception as e:
            print(f"Error in {func.__name__}: {e}")

    return wrapper


if __name__ == '__main__':

    jobs = [
        # runs every 10 minutes between 0–30 (as per your existing logic)
        (safe_job(main.schedule_print), 'telnet_job', 10, '0-30/10'),

        # runs at 10:31
        # (safe_job(main.check_file_uploads), 'file_check_job', 10, 31),

        # SFTP connection check
        # (safe_job(nse_sftp_connection.check_nse_sftp), 'sftp_job', 12, 17),

        # runs ONLY 2 times: 09:05 and 09:20
        # (safe_job(nse_sftp_market_hrs.check_nse_sftp_market_hrs), 'realtime_file_job', 14, '33,20'),

        # runs ONLY 2 times: 09:05 and 09:20
        # (safe_job(bse_sftp_markrt_hrs.check_bse_sftp_market_hrs), 'bse_master_trans_file', 16, '15,20'),

        #  NEW: DB check job (runs every 10 min from 9–18, Mon–Fri)
        # (safe_job(db_check.check_data_updated), 'db_check_job', 16, '15,20'),


    ]

    for func, job_id, hr, min_ in jobs:
        scheduler.add_job(
            func,
            trigger='cron',
            hour=hr,
            minute=min_,
            day_of_week='mon-fri',
            id=job_id,
            replace_existing=True
        )

    scheduler.start()
    print("Scheduler started...")

    atexit.register(lambda: scheduler.shutdown())

    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
