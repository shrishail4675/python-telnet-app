import subprocess
import config
from datetime import datetime

def check_nse_sftp():

    today_prefix = datetime.now().strftime("realtime_%d%m%Y")

    command = f"""
    {config.nse_command} <<EOF
    cd IN
    ls
    cd ../DONE
    ls
    bye
    EOF
    """

    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )

    output = result.stdout + result.stderr

    # Connection check
    if "Connected to" not in output:
        return "NSE SFTP Connection Failed\n" + output

    in_files = []
    done_files = []
    current_folder = None

    for line in output.splitlines():
        line = line.strip()

        if "cd IN" in line:
            current_folder = "IN"
            continue
        elif "cd ../DONE" in line:
            current_folder = "DONE"
            continue

        if line.startswith("realtime_"):
            if current_folder == "IN":
                in_files.append(line)
            elif current_folder == "DONE":
                done_files.append(line)

    # Check IN first
    for file in in_files:
        if file.startswith(today_prefix):
            return f"NSE Connected\nFiles Uploaded in IN folder"

    # Check DONE
    for file in done_files:
        if file.startswith(today_prefix):
            return f"NSE Connected\nFiles Uploaded in DONE folder"

    # If file not found → return standard output also
    return "NSE Connected but today's files NOT Uploaded in IN or DONE folder\n\nSFTP Output:\n" + output