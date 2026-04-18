import time
import socket
import os
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import config

import whatsapp_alert

scheduler = BackgroundScheduler()


#  TELNET SCHEDULER
def schedule_print():
    print(f"\n[TELNET CHECK] Time : {time.strftime('%A, %d %B %Y %I:%M:%S %p')}")

    try:
        for server in config.HOSTS:
            try:
                tcp_test, remote_address, source_address = telnet_connection(
                    server["host"], server["port"]
                )

                status = "SUCCESS" if tcp_test else "FAILED"

                message = (
                    f"\nComputerName     : {server['host']}\n"
                    f"RemoteAddress    : {remote_address}\n"
                    f"RemotePort       : {server['port']}\n"
                    f"SourceAddress    : {source_address}\n"
                    f"TcpTestSucceeded : {tcp_test} ({status})\n"
                    f"---------------------------------------------------"
                )

                print(message)
                # whatsapp_alert.send_whatsapp(message)

            except Exception as server_error:
                error_message = (
                    f"\nComputerName     : {server['host']}\n"
                    f"RemotePort       : {server['port']}\n"
                    f"Status           : ERROR\n"
                    f"Error            : {str(server_error)}\n"
                    f"---------------------------------------------------"
                )

                print(error_message)
                # whatsapp_alert.send_whatsapp(error_message)

    except Exception as e:
        fail_message = f"[TELNET CHECK FAILED]\nError: {str(e)}"
        print(fail_message)
        # whatsapp_alert.send_whatsapp(fail_message)


# ================= TELNET EXECUTION =================

def execute_connection(host_list):
    response = []

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

    return response


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

    today = datetime.now().strftime("%d%m%Y")  # 17042026
    missingfiles = []
    successful = []
    final_message = ""

    try:
        for etf in config.ETF_LIST:
            etfpath = os.path.join(config.base_path, etf, "IN")

            if not os.path.exists(etfpath):
                missingfiles.append(f"{etf} - IN folder missing")
                continue

            files = os.listdir(etfpath)

            comp_pattern = f"comp_{today}"
            const_pattern = f"const_{today}"

            comp_found = any(comp_pattern in f.lower() for f in files)
            const_found = any(const_pattern in f.lower() for f in files)

            if comp_found and const_found:
                successful.append(etf)
            else:
                if not comp_found:
                    missingfiles.append(f"{etf} - comp missing")
                if not const_found:
                    missingfiles.append(f"{etf} - const missing")

        # ================= SUMMARY =================
        print("\n------------------------ Result ------------------------")

        if missingfiles:
            final_message += "\nMissing ETF files:\n" + "\n".join(missingfiles) + "\n"

        if successful:
            final_message += "\nAll files present for ETFs:\n" + "\n".join(successful) + "\n"

        # If nothing was added
        if not final_message.strip():
            final_message = "No ETFs processed"

        print(final_message)

        # Send WhatsApp Alert
        # whatsapp_alert.send_whatsapp(final_message)

    except Exception as e:
        print(f"Error: {str(e)}")
