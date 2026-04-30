import pexpect
import config
from datetime import datetime
import re
import whatsapp_alert


def check_bse_sftp_market_hrs():
    child = None
    session_log = ""
    final_message = ""

    try:
        today = datetime.now()

        date_dash = today.strftime("%Y-%m-%d")
        date_nodash = today.strftime("%Y%m%d")

        pattern_main = re.compile(rf"^KOTAK_{date_dash}-\d{{2}}-\d{{2}}-\d{{2}}\.csv$")
        pattern_master = re.compile(rf"^KOTAK_MASTER_{date_nodash}\.csv$")

        # ---------------- START SFTP ----------------
        child = pexpect.spawn(
            config.bse_command,
            timeout=20,
            encoding="utf-8"
        )

        # ---------------- LOGIN ----------------
        child.expect(r"[Pp]assword:", timeout=10)
        session_log += (child.before or "") + "password:\n"
        child.sendline(config.bse_password)

        child.expect(r"sftp>", timeout=10)
        session_log += (child.before or "") + "sftp>\n"

        # ---------------- ROOT ----------------
        child.sendline("ls")
        child.expect(r"sftp>", timeout=10)
        root_output = child.before or ""
        session_log += "\n[ROOT LS OUTPUT]\n" + root_output + "\n"

        # ---------------- BACKUP ----------------
        child.sendline("cd backup")
        child.expect(r"sftp>", timeout=10)
        session_log += "\n[cd backup]\n" + (child.before or "") + "\n"

        child.sendline("ls")
        child.expect(r"sftp>", timeout=10)
        backup_output = child.before or ""
        session_log += "\n[BACKUP LS OUTPUT]\n" + backup_output + "\n"

        # Proper exit
        child.sendline("bye")
        child.expect(pexpect.EOF, timeout=10)

        # ---------------- PARSE FILES ----------------
        root_files = [f.strip() for f in root_output.splitlines() if f.strip()]
        backup_files = [f.strip() for f in backup_output.splitlines() if f.strip()]

        def check(files):
            main_found = any(pattern_main.match(f) for f in files)
            master_found = any(pattern_master.match(f) for f in files)
            return main_found, master_found

        root_main, root_master = check(root_files)
        backup_main, backup_master = check(backup_files)

        # ---------------- DECISION ----------------
        if root_main and root_master:
            final_message = "BSE SFTP Connected - Files found in ROOT folder"

        elif backup_main and backup_master:
            final_message = "BSE SFTP Connected - Files found in BACKUP folder"

        else:
            final_message = (
                "BSE SFTP ALERT - FILES MISSING\n"
                f"Root OK: {root_main and root_master}\n"
                f"Backup OK: {backup_main and backup_master}\n"
                "\nSESSION LOG:\n"
                f"{session_log}"
            )

    except pexpect.exceptions.TIMEOUT:
        final_message = (
            "BSE SFTP FAILED - TIMEOUT\n"
            "\nSESSION LOG:\n"
            f"{session_log}"
        )

    except pexpect.exceptions.EOF:
        final_message = (
            "BSE SFTP FAILED - CONNECTION CLOSED (EOF)\n"
            "\nSESSION LOG:\n"
            f"{session_log}"
        )

    except Exception as e:
        final_message = (
            f"BSE SFTP FAILED - ERROR: {str(e)}\n"
            "\nSESSION LOG:\n"
            f"{session_log}"
        )

    finally:
        if child is not None:
            try:
                child.close(force=True)
            except Exception:
                pass

        # ALWAYS SEND WHATSAPP ALERT
        # whatsapp_alert.send_whatsapp(final_message)

        print("\n------ BSE SFTP Response ------\n")
        print(final_message)