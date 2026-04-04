import pexpect
import config
from datetime import datetime


def check_bse_sftp():
    try:
        today_prefix = datetime.now().strftime("realtime_%d%m%Y")

        child = pexpect.spawn(config.bse_command, timeout=20)

        child.expect('password:')
        child.sendline(config.bse_password)

        child.expect('sftp>')

        # List root folder
        child.sendline('ls')
        child.expect('sftp>')
        root_output = child.before.decode()

        # Go to backup folder and list
        child.sendline('cd backup')
        child.expect('sftp>')

        child.sendline('ls')
        child.expect('sftp>')
        backup_output = child.before.decode()

        child.sendline('bye')

        # Parse files
        root_files = []
        backup_files = []

        for line in root_output.splitlines():
            line = line.strip()
            if line.startswith("realtime_"):
                root_files.append(line)

        for line in backup_output.splitlines():
            line = line.strip()
            if line.startswith("realtime_"):
                backup_files.append(line)

        # Check root first
        for file in root_files:
            if file.startswith(today_prefix):
                return f"BSE Connected\nFiles Uploaded in Root folder"

        # Then check backup
        for file in backup_files:
            if file.startswith(today_prefix):
                return f"BSE Connected\nFiles Uploaded in Backup folder"

        return "BSE Connected but today's files NOT Uploaded in Root or Backup"

    except Exception as e:
        return "BSE Connection Failed\n" + str(e)