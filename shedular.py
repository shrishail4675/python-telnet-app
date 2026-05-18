import db_check
import nse_sftp_market_hrs
import nse_sftp_morning
import atexit
import main
import config
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
        # runs every 10 minutes between 0–30 (as per your existing logic)Done
        # (safe_job(main.schedule_print(config.HOSTS)), 'telnet_job', 11, '0-59/1'),

        # runs every 10 minutes between 0–30 (as per your existing logic)Done
        # (safe_job(main.schedule_print(config.TickerMktUrl)), 'telnet_tickerUrl', 18, '0-59/1'),

        # runs at 10:31 Done
        # (safe_job(main.check_file_uploads), 'file_check_job', 17, 37),

        # SFTP connection check Done
        # (safe_job(nse_sftp_morning.check_nse_sftp), 'sftp_job', 17, 13),

        # runs ONLY 2 times: 09:05 and 09:20
        # (safe_job(nse_sftp_market_hrs.check_nse_sftp_market_hrs), 'realtime_file_job', 14, '33,20'),

        # runs ONLY 2 times: 09:05 and 09:20
        # (safe_job(bse_sftp_market_hrs.check_bse_sftp_market_hrs), 'bse_master_trans_file', 16, '15,20'),

        #  NEW: DB check job (runs every 10 min from 9 to 18, Mon–Fri)
        (safe_job(db_check.check_data_updated), 'db_check_job', 12, '38,20'),
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
