
import re

from file_handling import File
from common import W, Y, UL


def is_email_addr(email: str) -> bool:
    if match:= re.fullmatch("^[A-Za-z0-9._+\-\']+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$", email):
        return email == match.string
    print(f"{Y}[WARN] \"{UL}{email}{W}{Y}\": does not match email pattern, skipping ...{W}")
    return False


def get_mailing_list(raw_contacts: str, start_range: int = 1, end_range: int = 0) -> list[str]:
    contacts = []

    for i in [e.strip() for e in raw_contacts.split(",")]:
        i = i.strip().strip("\n")
        if File.is_file(i):
            for email in File(i).readlines():
                email = email.strip("\n").split(":")[0].strip()
                if email.startswith("#"):
                    continue
                if is_email_addr(email):
                    if not email in contacts:
                        contacts.append(email)
        elif is_email_addr(i):
            if not i in contacts:
                contacts.append(i)

    assert start_range >= 1, "start_range >= 1"
    end_range = len(contacts) if end_range == 0 or end_range > len(contacts) else end_range
    assert start_range <= end_range, "start_range <= end_range"

    contacts = contacts[start_range-1:end_range]
    print(f"[INFO] range: [{start_range} - {end_range}]")
    print(f"[INFO] Emails Count: {len(contacts)}")
    return contacts
