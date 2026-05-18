# telnet host & ips
HOSTS = [
    {"host": "com.visvbcvnualstudio.com", "port": 443},
    {"host": "gotestogle.com", "port": 443},
    {"host": "gitcxbcvhub.com", "port": 443}
]
TickerMktUrl = [
    {"host": "com.visualstudio.com", "port": 443},
    {"host": "google.com", "port": 443},
    {"host": "github.com", "port": 443}
]

# NSE SFTP Command --Morning
nse_primary_command = "sftp -i /home/appadmin/.ssh/id_rsa -oport=6010 KOTAKINAV@125.22.48.105"
nse_secondary_command = "sftp -i /home/appadmin/.ssh/id_rsa -oport=6010 KOTAKINAV@125.22.48.106"

# NSE SFTP Command --Market Hours
nse_primary_markethrs_command=""
nse_secondary_markethrs_command=""

# BSE SFTP Command & Password
bse_command = 'sftp -i /home/appadmin/.ssh/id_rsa -oport=6010 KOTAKINAV@125.22.48.106'
bse_password = 'March$2026'

# base path of all uploaded files
# base_path = "/home/navApplication/"
base_path = "C:/Users/sande/Downloads/Sample_Files/"

ETF_LIST = [
    "ALPHA50NAV",
    "Nifty200Momentum30ETF",
    "BANKINGNAV",
    "Nifty200Qty30",
    "PSUBANKNAV",
    "NV20ETFNAV",
    "NIFTYNAV",
    "NIFTYMIDCAP150",
    "NIFTYINDIACONSNAV",
    "NIFTY100LOWVOL30NAV",
    "NIFTY100equalWeightETF",
    "MSCI_INDIA_ETF",
    "MIDCAP50NAV",
    "CHEMICAL",
    "KOTAKNIFTYKMNCNAV",
    "ITETFNAV",
    "KotakNiftyNext50ETF"
]

# NSE file check
file_prefixes = [
    "CHEMICAL", "KOTAKALPHA", "KOTAKBKETF", "KOTAKCONS", "KOTAKITETF", "KOTAKLOVOL", "KOTAKMID50",
    "KOTAKMNC", "yz1", "yz2", "yz3", "yz4", "yz5",
    "yz6", "yz7", "yz8", "yz9"
]

# Whatsapp api details
API_KEY = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJrb3Rha19hbWNfZWFwaXw3MDQ1MDk1NzcxIiwiZXhwIjoyNjA5NDc4NTc4fQ.zVpayaky-xHmDB5vsJgk0NvMx-i9rmx_e76rNXM8G1O5I_VLsb4YfOQjyAunwlQ1k3i2UlkpQo9qjLrMUvmK0Q"
URL = "https://waapi.pepipost.com/api/v2/message/"
TO_NUMBERS = [
    "918766771695",
    "918879100819"
]
