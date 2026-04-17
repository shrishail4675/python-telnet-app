import time
import socket
import os
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import config

import whatsapp_alert

scheduler = BackgroundScheduler()
retry_job = None
failed_hosts = []

#  TELNET SCHEDULER

def schedule_print():
    global retry_job, \
        failed_hosts

    print(f"\n[TELNET CHECK] Time : {time.strftime('%A, %d %B %Y %I:%M:%S %p')}")

    failed_hosts = execute_connection(config.HOSTS)

    if failed_hosts:
        print("Some connections failed. Starting retry job...")
        if retry_job is None:
            retry_job = scheduler.add_job(
                retry_connection,
                trigger='interval',
                seconds=config.RETRY_INTERVAL_SECONDS,
                id='retry_job',
                replace_existing=True
            )


# ================= RETRY LOGIC =================

def retry_connection():
    global retry_job, failed_hosts

    print("\n[RETRY] Retrying failed connections...")

    failed_hosts = execute_connection(failed_hosts)

    if not failed_hosts:
        print("All connections successful. Stopping retry job.")
        scheduler.remove_job('retry_job')
        retry_job = None


# ================= TELNET EXECUTION =================

def execute_connection(host_list):
    failed = []

    for server in host_list:
        tcp_test, remote_address, source_address = telnet_connection(
            server["host"], server["port"]
        )

        message = (
            f"\nComputerName     : {server['host']}\n"
            f"RemoteAddress    : {remote_address}\n"
            f"RemotePort       : {server['port']}\n"
            f"SourceAddress    : {source_address}\n"
            f"TcpTestSucceeded : {tcp_test}\n"
            f"---------------------------------------------------"
        )

        print(message)

        # Send WhatsApp Alert (optional)
        # whatsapp_alert.send_whatsapp(message)

        if not tcp_test:
            failed.append(server)

    return failed


# ================= TELNET CONNECTION =================

def telnet_connection(host, port):
    try:
        addr_info = socket.getaddrinfo(host, port)
        remote_address = addr_info[0][4][0]

        sock = socket.create_connection((host, port), timeout=5)
        source_address = sock.getsockname()[0]
        sock.close()

        tcp_test = True
    except Exception:
        remote_address = "N/A"
        source_address = "N/A"
        tcp_test = False

    return tcp_test, remote_address, source_address

# ================= FILE CHECK SCHEDULER =================

def check_file_uploads():
    print(f"\n[FILE CHECK] Time : {time.strftime('%A, %d %B %Y %I:%M:%S %p')}")
    # print("---------------------------------------------------------")

    today = datetime.now().strftime("%d%m%Y")  # 17042026
    missingfiles = []
    successful = []

    try:
        for etf in config.ETF_LIST:
            etfpath = os.path.join(config.base_path, etf, "IN")
            # print(f"\nChecking ETF: {etf}")

            if not os.path.exists(etfpath):
                # print(f"[FAILED] IN folder missing for : {etf}")
                missingfiles.append(f"{etf} - IN folder missing")
                continue

            files = os.listdir(etfpath)
            # print("FILES:", files)

            # Check only required pattern (ignore prefix like xy_)
            comp_pattern = f"comp_{today}"
            const_pattern = f"const_{today}"

            comp_found = any(comp_pattern in f.lower() for f in files)
            const_found = any(const_pattern in f.lower() for f in files)

            if comp_found and const_found:
                # print(f"[SUCCESS] Both files present for : {etf}")
                successful.append(etf)
            else:
                if not comp_found:
                    # print(f"[FAILED] comp file missing for : {etf}")
                    missingfiles.append(f"{etf} - comp missing")

                if not const_found:
                    # print(f"[FAILED] const file missing for : {etf}")
                    missingfiles.append(f"{etf} - const missing")

        # ================= SUMMARY =================
        print("\n------------------------ Result ------------------------")

        if missingfiles:
            message = "\nMissing ETF files:\n" + "\n".join(missingfiles)
            print(message)

            # Send WhatsApp Alert
            # whatsappalert.sendwhatsapp(message)

        if successful:
            success_message = "\nAll files present for ETFs:\n" + "\n".join(successful)
            print(success_message)

            # Send WhatsApp Alert
            # whatsappalert.sendwhatsapp(success_message)

        if not missingfiles and not successful:
            print("No ETFs processed")

    except Exception as e:
        print(f"Error: {str(e)}")