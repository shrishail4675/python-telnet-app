import nse_sftp_connection
import bse_sftp_connection
import whatsapp_alert

from apscheduler.schedulers.background import BackgroundScheduler

def check_all_sftp():

    print("Shedular calling nse and bse sftp methods")

    nse_output = nse_sftp_connection.check_nse_sftp()
    whatsapp_alert.send_whatsapp("NSE SFTP:\n" + nse_output)

    bse_output = bse_sftp_connection.check_bse_sftp()
    whatsapp_alert.send_whatsapp("BSE SFTP:\n" + bse_output)
