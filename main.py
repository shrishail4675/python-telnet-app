import time
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import socket


from flask import Flask
from pythonping import ping

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/hello')
def hello_fun():
    return 'Hello'

def schedule_print():
    print(time.strftime("%w %m %Y %H:%M:%S"))
    print(time.strftime("%A, %d. %B %Y %I:%M:%S %p"))
    # ping('code.visualstudio.com', verbose=True)
    test_net_connection("com.visualstudio.com", 443)

def test_net_connection(host, port):
    try:
        # Resolve IP address
        addr_info = socket.getaddrinfo(host, port)
        remote_address = addr_info[0][4][0]

        # Get source address
        sock = socket.create_connection((host, port), timeout=5)
        source_address = sock.getsockname()[0]
        sock.close()

        tcp_test = True
    except Exception:
        remote_address = "N/A"
        source_address = "N/A"
        tcp_test = False

    print(f"ComputerName     : {host}")
    print(f"RemoteAddress    : {remote_address}")
    print(f"RemotePort       : {port}")
    print(f"SourceAddress    : {source_address}")
    print(f"TcpTestSucceeded : {tcp_test}")


scheduler = BackgroundScheduler()
scheduler.add_job(func=schedule_print, trigger="interval", seconds=59)
scheduler.start()

if __name__ == '__main__':
    app.run()