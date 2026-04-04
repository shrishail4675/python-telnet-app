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
    print("---------------------------------------------------------")

    today_folder = datetime.now().strftime("%d-%m-%Y")
    today_file_prefix = datetime.now().strftime("realtime_%d%m%Y")

    missing_files = []

    try:
        etf_list = os.listdir(config.base_path)

        for etf in etf_list:
            etf_path = os.path.join(config.base_path, etf)

            if not os.path.isdir(etf_path):
                continue

            for market in ["NSE", "BSE"]:
                market_path = os.path.join(etf_path, market, today_folder)

                if os.path.exists(market_path):
                    files = os.listdir(market_path)

                    file_found = any(file.startswith(today_file_prefix) for file in files)

                    if file_found:
                        print(f"[SUCCESS] File Uploaded for : {etf} / {market}")
                    else:
                        print(f"[FAILED] File missing for : {etf} / {market}")
                        missing_files.append(f"{etf} - {market}")

                else:
                    print(f"[FAILED] Date folder missing : {etf} / {market}")
                    missing_files.append(f"{etf} - {market}")

        # Final Summary
        print("\n------------------------ SUMMARY ------------------------")

        if missing_files:
            print("Files missing in below folders:")
            for m in missing_files:
                print(m)

            # whatsapp_alert.send_whatsapp("Missing files:\n" + "\n".join(missing_files))
        else:
            print("All ETF files uploaded successfully")
            # whatsapp_alert.send_whatsapp("All ETF files uploaded successfully")

    except Exception as e:
        print(f"Error: {str(e)}")