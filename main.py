import time
import socket
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
import config
import whatsapp_alert

app = Flask(__name__)

scheduler = BackgroundScheduler()
retry_job = None
failed_hosts = []


@app.route('/')
def hello_world():
    return 'Hello World!'


def schedule_print():
    global retry_job, failed_hosts

    print(f"cronTime : {time.strftime('%A, %d %B %Y %I:%M:%S %p')}")

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


def retry_connection():
    global retry_job, failed_hosts

    print("Retrying failed connections...")

    failed_hosts = execute_connection(failed_hosts)

    if not failed_hosts:
        print("All connections successful. Stopping retry job.")
        scheduler.remove_job('retry_job')
        retry_job = None


def execute_connection(host_list):
    failed = []

    for server in host_list:
        tcp_test, remote_address, source_address = telnet_connection(server["host"], server["port"])

        # Create message
        message = (
            f"ComputerName     : {server['host']}\n"
            f"RemoteAddress    : {remote_address}\n"
            f"RemotePort       : {server['port']}\n"
            f"SourceAddress    : {source_address}\n"
            f"TcpTestSucceeded : {tcp_test}\n"
            f"---------------------------------------------------"
        )

        print(message)

        # Send WhatsApp message(Uncomment these line)
        # whatsapp_alert.send_whatsapp(message)

        if not tcp_test:
            failed.append(server)

    return failed


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


if __name__ == '__main__':
    scheduler.add_job(
        schedule_print,
        trigger='cron',
        hour=config.CRON_HOUR,
        minute=config.CRON_MINUTE,
        id='daily_job',
        replace_existing=True
    )

    scheduler.start()

    app.run(debug=False)