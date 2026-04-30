import pexpect
import config
from datetime import datetime
import re
import whatsapp_alert  # assuming this is your module


def check_bse_sftp_market_hrs():
    child = None
    session_log = ""

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

        child.expect("password:", timeout=10)
        session_log += child.before + "password:\n"
        child.sendline(config.bse_password)

        child.expect("sftp>", timeout=10)
        session_log += child.before + "sftp>\n"

        # ---------------- ROOT ----------------
        child.sendline("ls")
        child.expect("sftp>", timeout=10)
        root_output = child.before
        session_log += "\n[ROOT LS OUTPUT]\n" + root_output + "\n"

        # ---------------- BACKUP ----------------
        child.sendline("cd backup")
        child.expect("sftp>", timeout=10)
        session_log += "\n[cd backup]\n" + child.before + "\n"

        child.sendline("ls")
        child.expect("sftp>", timeout=10)
        backup_output = child.before
        session_log += "\n[BACKUP LS OUTPUT]\n" + backup_output + "\n"

        child.sendline("bye")

        # ---------------- PARSE FILES ----------------
        root_files = [f.strip() for f in root_output.splitlines() if f.strip()]
        backup_files = [f.strip() for f in backup_output.splitlines() if f.strip()]

        def check(files):
            main_found = any(pattern_main.match(f) for f in files)
            master_found = any(pattern_master.match(f) for f in files)
            return main_found, master_found

        root_main, root_master = check(root_files)
        backup_main, backup_master = check(backup_files)

        # ---------------- FINAL LOGIC ----------------
        if root_main and root_master:
            final_message = (
                "BSE SFTP CONNECTED\n"
                "Status: Files found in ROOT folder\n"
                f"Main File: {root_main}\n"
                f"Master File: {root_master}"
            )

        elif backup_main and backup_master:
            final_message = (
                "BSE SFTP CONNECTED\n"
                "Status: Files found in BACKUP folder\n"
                f"Main File: {backup_main}\n"
                f"Master File: {backup_master}"
            )

        else:
            final_message = (
                "BSE SFTP CONNECTED BUT FILES MISSING\n"
                f"Root OK: {root_main and root_master}\n"
                f"Backup OK: {backup_main and backup_master}"
            )

        final_message += "\n\n===== SESSION LOG =====\n" + session_log

        whatsapp_alert.send_whatsapp(final_message)

        return final_message

    except pexpect.exceptions.TIMEOUT:
        final_message = (
                "BSE SFTP FAILED - TIMEOUT\n\n"
                + session_log
        )
        whatsapp_alert.send_whatsapp(final_message)

        return final_message

    except pexpect.exceptions.EOF:
        final_message = (
                "BSE SFTP FAILED - CONNECTION CLOSED (EOF)\n\n"
                + session_log
        )
        whatsapp_alert.send_whatsapp(final_message)

        return final_message

    except Exception as e:
        final_message = (
                f"BSE SFTP FAILED - ERROR\nReason: {str(e)}\n\n"
                + session_log
        )
        whatsapp_alert.send_whatsapp(final_message)
        return final_message

    finally:
        if child is not None:
            try:
                child.close(force=True)
            except:
                pass
