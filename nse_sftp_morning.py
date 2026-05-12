import subprocess
from datetime import datetime
import config
import whatsapp_alert

TOTAL_EXPECTED_FILES = 34


def check_nse_sftp():
    final_output = []

    current_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    final_output.append(f"         Checking files on NSE Primary & Secondary Servers @ {current_time}")
    # PRIMARY SERVER

    primary_result = check_server(
        "PRIMARY",
        config.nse_primary_command
    )

    # SECONDARY SERVER
    secondary_result = check_server(
        "SECONDARY",
        config.nse_secondary_command
    )

    final_output.append(
        print_final_summary(primary_result, secondary_result)
    )

    final_message = "\n".join(final_output)

    # print("\n")
    # print(final_message)

    # SEND WHATSAPP MESSAGE
    whatsapp_alert.send_whatsapp(final_message)

    return final_message


def run_sftp(command):
    try:

        if not command or not command.strip():
            return {
                "success": False,
                "output": "",
                "error": "SFTP command is empty"
            }

        cmd = f"""
        {command} <<EOF
        cd IN
        ls
        bye
        EOF
        """

        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )

        output = (
                (result.stdout or "") +
                (result.stderr or "")
        )

        output_lower = output.lower()

        error_keywords = [
            "permission denied",
            "connection refused",
            "connection closed",
            "couldn't",
            "not found",
            "failure",
            "network error",
            "authentication failed",
            "host key verification failed",
            "no such file",
            "invalid command",
            "cannot",
            "closed by remote host"
        ]

        for err in error_keywords:

            if err in output_lower:
                return {
                    "success": False,
                    "output": output,
                    "error": err
                }

        # =================================================
        # CONNECTION VALIDATION
        # =================================================
        success_keywords = [
            "connected to",
            "sftp>"
        ]

        connected = any(
            keyword in output_lower
            for keyword in success_keywords
        )

        if not connected:
            return {
                "success": False,
                "output": output,
                "error": "SFTP connection validation failed"
            }

        # =================================================
        # SUCCESS
        # =================================================
        return {
            "success": True,
            "output": output,
            "error": None
        }

    except subprocess.TimeoutExpired:

        return {
            "success": False,
            "output": "",
            "error": "SFTP Connection Timeout"
        }

    except Exception as e:

        return {
            "success": False,
            "output": "",
            "error": str(e)
        }


def check_server(server_name, command):
    today_date = datetime.now().strftime("%d%m%Y")

    result = run_sftp(command)

    if not result["success"]:
        return {
            "server": server_name,
            "connected": False,
            "reason": result["error"],
            "uploaded_files": [],
            "missing_files": [],
            "found_count": 0,
            "total_count": TOTAL_EXPECTED_FILES
        }

    output = result["output"]

    uploaded_files = []
    missing_files = []

    files_list = []

    for line in output.splitlines():

        filename = line.strip()

        if filename:
            files_list.append(filename)

    for prefix in config.file_prefixes:

        expected_files = [
            f"{prefix}_const_{today_date}",
            f"{prefix}_comp_{today_date}"
        ]

        for expected_file in expected_files:

            found = False

            for filename in files_list:

                if filename.startswith(expected_file):
                    found = True
                    uploaded_files.append(filename)
                    break

            if not found:
                missing_files.append(expected_file)

    return {
        "server": server_name,
        "connected": True,
        "reason": "",
        "uploaded_files": uploaded_files,
        "missing_files": missing_files,
        "found_count": len(uploaded_files),
        "total_count": TOTAL_EXPECTED_FILES
    }


def print_final_summary(primary_result, secondary_result):
    summary = []
    summary.append("--------------------------------------------------------------------------------------------")
    # PRIMARY SERVER
    summary.append("PRIMARY SERVER")

    if primary_result["connected"]:
        summary.append("SFTP CONNECTED SUCCESSFULLY")
        summary.append(
            f"FILES FOUND : "
            f"{primary_result['found_count']}/"
            f"{primary_result['total_count']}"
        )

        if primary_result["uploaded_files"]:

            summary.append("")
            summary.append("UPLOADED FILES:")

            for file in primary_result["uploaded_files"]:
                summary.append(f"{file}")

        if primary_result["missing_files"]:
            summary.append("")
            summary.append("MISSING FILES:")

            for file in primary_result["missing_files"]:
                summary.append(f"{file}")
        else:
            summary.append("")
            summary.append("ALL FILES UPLOADED SUCCESSFULLY")

    else:

        summary.append("SFTP CONNECTION FAILED")
        summary.append(f"REASON : {primary_result['reason']}")

    summary.append("")
    summary.append("SECONDARY SERVER")

    if secondary_result["connected"]:

        summary.append("SFTP CONNECTED SUCCESSFULLY")

        summary.append(
            f"FILES FOUND : "
            f"{secondary_result['found_count']}/"
            f"{secondary_result['total_count']}"
        )

        if secondary_result["uploaded_files"]:

            summary.append("")
            summary.append("UPLOADED FILES:")

            for file in secondary_result["uploaded_files"]:
                summary.append(f"{file}")

        if secondary_result["missing_files"]:

            summary.append("")
            summary.append("MISSING FILES:")

            for file in secondary_result["missing_files"]:
                summary.append(f"{file}")

        else:

            summary.append("")
            summary.append("ALL FILES UPLOADED SUCCESSFULLY")

    else:

        summary.append("SFTP CONNECTION FAILED")
        summary.append(f"REASON : {secondary_result['reason']}")
    return "\n".join(summary)

#
# if __name__ == "__main__":
#
#     try:
#
#         check_nse_sftp()
#
#     except KeyboardInterrupt:
#
#         print("Program Interrupted")
#
#     except Exception as e:
#
#         print(f"Unexpected Error : {str(e)}")
