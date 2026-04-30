import subprocess
import config
import whatsapp_alert
from datetime import datetime


def check_nse_sftp_market_hrs():
    final_message = ""

    try:
        today_str = datetime.now().strftime("%d%m%Y")
        search_pattern = f"realtime{today_str}"

        def run_sftp(command):
            cmd = f"""
            {command} <<EOF
            cd DONE
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
            return (result.stdout or "") + (result.stderr or "")

        primary_output = run_sftp(config.nse_primary_markethrs_command)
        secondary_output = run_sftp(config.nse_secondary_markethrs_command)

        def analyze(output):
            output_clean = output.strip()

            # Connection failed
            if "Connected to" not in output:
                return {
                    "status": "CONNECTION_FAILED",
                    "error": output_clean[:500]
                }

            files = [line.strip() for line in output.splitlines()]

            realtime_files = [f for f in files if search_pattern in f]

            csv_files = [f for f in realtime_files if f.endswith(".csv")]
            trg_files = [f for f in realtime_files if f.endswith(".csv.trg")]

            # No files at all
            if not realtime_files:
                return {
                    "status": "NO_FILES",
                    "error": output_clean[:300]
                }

            # Only SUCCESS if BOTH exist
            if csv_files and trg_files:
                return {
                    "status": "SUCCESS",
                    "csv_count": len(csv_files),
                    "trg_count": len(trg_files)
                }

            # Treat missing pair as NO_FILES (no partial state)
            return {
                "status": "NO_FILES",
                "error": output_clean[:300]
            }

        primary = analyze(primary_output)
        secondary = analyze(secondary_output)

        # ---------------- MESSAGE ---------------- #

        final_message = "NSE REALTIME SFTP MONITOR (DONE FOLDER)\n\n"

        def build_block(name, res):
            msg = f"{name} SERVER:\n"

            if res["status"] == "SUCCESS":
                msg += (
                    "SUCCESS\n"
                    f"CSV Files: {res['csv_count']}\n"
                    f"TRG Files: {res['trg_count']}\n\n"
                )

            elif res["status"] == "NO_FILES":
                msg += (
                    "NO VALID REALTIME FILES\n"
                    "CSV/TRG pair not found for today\n"
                )
                msg += f"\nRaw Response:\n{res['error']}\n\n"

            elif res["status"] == "CONNECTION_FAILED":
                msg += "CONNECTION FAILED\n"
                msg += f"\nRaw Response:\n{res['error']}\n\n"

            return msg

        final_message += build_block("PRIMARY", primary)
        final_message += build_block("SECONDARY", secondary)

        # ---------------- OVERALL ---------------- #

        if primary["status"] == "SUCCESS" and secondary["status"] == "SUCCESS":
            final_message += "OVERALL: Realtime feed is running on BOTH servers"

        elif primary["status"] == "SUCCESS":
            final_message += "OVERALL: Realtime feed running only on PRIMARY"

        elif secondary["status"] == "SUCCESS":
            final_message += "OVERALL: Realtime feed running only on SECONDARY"

        else:
            final_message += "OVERALL: Realtime feed DOWN on both servers"

    except subprocess.TimeoutExpired as e:
        partial_output = (e.stdout or "") + (e.stderr or "")

        final_message = (
            "ALERT: NSE SFTP TIMEOUT\n"
            "Connection exceeded 60 seconds.\n\n"
            f"Partial Response:\n{partial_output[:500]}"
        )

    except Exception as e:
        final_message = (
            "ALERT: Unexpected Error\n"
            f"{str(e)}"
        )

    # ALWAYS SEND ALERT
    try:
        print(final_message)
        # whatsapp_alert.send_whatsapp(final_message)
    except Exception as e:
        print("Failed to send WhatsApp alert:", str(e))

    return final_message