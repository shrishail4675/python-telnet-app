import time
import socket
import os
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import config
import subprocess

import whatsapp_alert

scheduler = BackgroundScheduler()


#  TELNET SCHEDULER

def check_connectivity(host, port):

    try:

        command = ["nc", "-zv", host, str(port)]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=10
        )

        # Capture exact response
        response = (
            result.stderr.strip()
            if result.stderr.strip()
            else result.stdout.strip()
        )

        # SUCCESS
        if result.returncode == 0:
            return True, f"SUCCESS : {response}"

        # COMMON FAILURES
        response_lower = response.lower()

        if "connection refused" in response_lower:
            return False, f"Connection Refused : {response}"

        elif "timed out" in response_lower:
            return False, f"Connection Timed Out : {response}"

        elif "no route to host" in response_lower:
            return False, f"No Route To Host : {response}"

        elif "name or service not known" in response_lower:
            return False, f"DNS Resolution Failed : {response}"

        elif "temporary failure in name resolution" in response_lower:
            return False, f"DNS Temporary Failure : {response}"

        elif "network is unreachable" in response_lower:
            return False, f"Network Unreachable : {response}"

        elif "operation now in progress" in response_lower:
            return False, f"Operation In Progress : {response}"

        elif "invalid argument" in response_lower:
            return False, f"Invalid Host/Port : {response}"

        elif "permission denied" in response_lower:
            return False, f"Permission Denied : {response}"

        elif "unknown host" in response_lower:
            return False, f"Unknown Host : {response}"

        # Generic failure
        return False, f"FAILED : {response}"

    except subprocess.TimeoutExpired:
        return False, "TimeoutExpired : Connection Timeout After 10 Seconds"

    except FileNotFoundError:
        return False, "nc command not found on Linux server"

    except socket.gaierror as e:
        return False, f"Socket Address Error : {str(e)}"

    except socket.timeout:
        return False, "Socket Timeout"

    except ConnectionRefusedError:
        return False, "Python Connection Refused"

    except PermissionError:
        return False, "Permission Denied"

    except OSError as e:
        return False, f"OS Error : {str(e)}"

    except Exception as e:
        return False, f"Unexpected Error : {str(e)}"


def schedule_print(hosts):

    print(
        f"\n[CONNECTIVITY CHECK] Time : "
        f"{time.strftime('%d/%m/%Y %I.%M.%S %p')}"
    )

    try:

        for server in hosts:

            host = server.get("host")
            port = server.get("port")

            try:

                # Validate input
                if not host:
                    raise ValueError("Host is missing")

                if not port:
                    raise ValueError("Port is missing")

                tcp_test, response = check_connectivity(host, port)

                status = "SUCCESS ✅" if tcp_test else "FAILED ❌"

                message = (
                    f"\nComputerName     : {host}\n"
                    f"RemotePort       : {port}\n"
                    f"Status           : {status}\n"
                    f"Response         : {response}\n"
                    f"---------------------------------------------------"
                )

                print(message)

                # WHATSAPP ALERT
                whatsapp_alert.send_whatsapp(
                    template_name="connectivity_notification_inav",
                    attributes=[
                        status,
                        f"{host}:{port} at "
                        f"{time.strftime('%d/%m/%Y %I.%M.%S %p')}",
                        response
                    ]
                )

            except ValueError as ve:

                error_message = (
                    f"\nInvalid Configuration\n"
                    f"Host  : {host}\n"
                    f"Port  : {port}\n"
                    f"Error : {str(ve)}\n"
                    f"---------------------------------------------------"
                )

                print(error_message)

                whatsapp_alert.send_whatsapp(
                    template_name="connectivity_notification_inav",
                    attributes=[
                        "FAILED ❌",
                        f"{host}:{port}",
                        str(ve)
                    ]
                )

            except Exception as server_error:

                error_message = (
                    f"\nComputerName     : {host}\n"
                    f"RemotePort       : {port}\n"
                    f"Status           : FAILED ❌\n"
                    f"Unhandled Error  : {str(server_error)}\n"
                    f"---------------------------------------------------"
                )

                print(error_message)

                whatsapp_alert.send_whatsapp(
                    template_name="connectivity_notification_inav",
                    attributes=[
                        "FAILED ❌",
                        f"{host}:{port}",
                        f"Unhandled Error : {str(server_error)}"
                    ]
                )

    except KeyboardInterrupt:

        print("\nProcess Interrupted By User")

        whatsapp_alert.send_whatsapp(
            template_name="connectivity_notification_inav",
            attributes=[
                "FAILED ❌",
                "Scheduler Interrupted",
                "Process Interrupted By User"
            ]
        )

    except Exception as e:

        fail_message = (
            f"\n[CONNECTIVITY CHECK FAILED]\n"
            f"Error : {str(e)}"
        )

        print(fail_message)

        whatsapp_alert.send_whatsapp(
            template_name="connectivity_notification_inav",
            attributes=[
                "FAILED ❌",
                "Scheduler Error",
                str(e)
            ]
        )
# ================= TELNET CONNECTION =================

# def telnet_connection(host, port):
#     try:
#         addr_info = socket.getaddrinfo(host, port)
#         remote_address = addr_info[0][4][0]
#
#         sock = socket.create_connection((host, port), timeout=5)
#         source_address = sock.getsockname()[0]
#         sock.close()
#
#         tcp_test = True
#     except Exception:
#         remote_address = "N/A"
#         source_address = "N/A"
#         tcp_test = False
#
#     return tcp_test, remote_address, source_address


def check_file_uploads():
    print(f"\n[FILE CHECK] Time : {time.strftime('%A, %d %B %Y %I:%M:%S %p')}")

    today = datetime.now().strftime("%d%m%Y")

    missingfiles = []
    successful = []

    total_files_generated = 0
    total_expected_files = len(config.ETF_LIST) * 2  # comp + const

    try:

        for etf in config.ETF_LIST:

            etfpath = os.path.join(config.base_path, etf, "IN")

            if not os.path.exists(etfpath):
                missingfiles.append(f"{etf} - IN folder missing")
                continue

            files = os.listdir(etfpath)

            comp_found = any(f"comp_{today}" in f.lower() for f in files)
            const_found = any(f"const_{today}" in f.lower() for f in files)

            # Count generated files
            if comp_found:
                total_files_generated += 1

            if const_found:
                total_files_generated += 1

            if comp_found and const_found:
                successful.append(etf)

            else:
                if not comp_found:
                    missingfiles.append(f"{etf} - comp missing")

                if not const_found:
                    missingfiles.append(f"{etf} - const missing")

        # current_time = time.strftime('%A, %d %B %Y %I:%M:%S %p')
        current_time = time.strftime('%d/%m/%Y %I.%M.%S %p')

        # SUCCESS TEMPLATE
        if total_files_generated == total_expected_files:
            whatsapp_alert.send_whatsapp(
                template_name="files_verification_success_inav",
                attributes=[
                    f"{total_files_generated}/{total_expected_files} as on {current_time} ✅",
                    "",
                    ""
                ]
            )

        # FAILURE TEMPLATE
        if missingfiles:
            whatsapp_alert.send_whatsapp(
                template_name="files_verification_failure_inav",
                attributes=[
                    f"Missing Files: {len(missingfiles)}/{total_expected_files}  as on {current_time} ❌",
                    "",
                    ""
                ]
            )

        # NOTHING PROCESSED
        if total_files_generated == 0 and not missingfiles:
            whatsapp_alert.send_whatsapp(
                template_name="files_verification_failure_inav",
                attributes=[
                    f"No ETFs Processed : 0/{total_expected_files}  as on {current_time} ❌",
                    "",
                    ""
                ]
            )

    except Exception as e:
        print(f"Error: {str(e)}")
