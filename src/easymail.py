
import time, smtplib, sys, shutil
from email.message import EmailMessage

from common import *
from consts import *
from mailing_list import *


class EasyMail:
    class MessageBlockedReason(enum.Enum):
        Allowed = 0
        BlackListedDestination = 1
        SpamProtectionPeriod = 2
    
    def __init__(self, account: AccountConfig, settings: EasyMailSettings, **kw) -> None:
        self.account = account
        self.settings = settings
        self.smtp_server = smtplib.SMTP(self.account.SMTP_server, self.account.port, timeout= self.account.timeout)
        self.success, self.refused, self.forced, self.black_listed, self.spam_protection = 0, 0, 0, 0, 0
        self.black_list = json.loads(File(kw["black_list"]).read_file()) if kw.get("black_list") else [] 

    def send_email(self, to: list[str] | str, contents: EmailMessageContents)-> None:
        if isinstance(to, str): to = [to]
        elif not isinstance(to, list): raise TypeError("to must be either a str ot list[str]")
        count = len(to)
        with self.smtp_server as smtp:
            self._log_in(smtp)
            for i, contact in enumerate(to):
                msg = contents.construct_email_message(contact)
                ts = load_timestamp("./timestamp.json")
                block_reason = EasyMail.MessageBlockedReason.Allowed

                if contact in self.black_list:
                    block_reason = EasyMail.MessageBlockedReason.BlackListedDestination

                if contact in ts.keys():
                    if delta_ts:= delta_time_hrs(ts.get(contact)) < 24.:
                        block_reason = EasyMail.MessageBlockedReason.SpamProtectionPeriod

                color, action, details= "", "", ""

                if block_reason == EasyMail.MessageBlockedReason.Allowed or self.settings.force_sending:
                    self._send(smtp, contact, msg, ind=i, count=count)
                    color = G
                    if block_reason != EasyMail.MessageBlockedReason.Allowed:
                        action = "Forced"
                        self.forced += 1
                    else:
                        action = "Sent"
                        self.success += 1
                else:
                    match block_reason:
                        case EasyMail.MessageBlockedReason.BlackListedDestination:
                            self.black_listed += 1
                            action = "Black Listed"
                            color = R
                        case EasyMail.MessageBlockedReason.SpamProtectionPeriod:
                            self.spam_protection += 1
                            action = "Spam Protection"
                            details = f'", delta time {delta_time_hrs(datetime.now().strftime(DATE_TIME_FORMAT)):.2f} hrs'
                            color = Y

                print(color + f'[{i+1:0>3}-{count:0>3}] {action}: "' + UL + contact + W + color + '"' + details + W)

        print("[INFO] Connection closed...")

    def _send(self, smtp: smtplib.SMTP, to: str, email_msg: EmailMessage, **kwargs) -> None:
        try:
            smtp.send_message(email_msg, rcpt_options=['NOTIFY=SUCCESS,DELAY,FAILURE'] if self.settings.delivery_report else None)
            update_timestamp("./timestamp.json" ,to)
            time.sleep(0.5)

        except smtplib.SMTPRecipientsRefused as e:
            self.refused += 1
            print(R + f"[SMTP ERROR] [{kwargs['ind']+1:0>3}-{kwargs['count']:0>3}] Refused: " + UL + to + W)
            print(R + "Reason:", e + W)

        except Exception as e:
            print(R + "[SMTP ERROR]",  e, W)
            raise e

    def _log_in(self, smtp: smtplib.SMTP) -> None:
            try:
                smtp.starttls()
                print("[INFO] Logging in...")
                smtp.login(self.account.email.strip(), self.account.password.strip())
            except Exception as e:
                print(R + f"[SMTP ERROR]", e, W)
                sys.exit()

    def log_report(self) -> None:
        report_header          ="+++++++++++++++++++REPORT++++++++++++++++++"
        report_suc             = f"| Report: {self.success} email(s) successfully sent."
        report_spam_protection = f"| Report: {self.spam_protection} email(s) in spam protection."
        report_black_listed    = f"| Report: {self.black_listed} email(s) in black list."
        report_forced          = f"| Report: {self.forced} email(s) forced."
        report_refused         = f"| Report: {self.refused} email(s) refused."
        _time                  = f"| {datetime.now()}".split(".")[0]
        report_footer          ="+++++++++++++++++++++++++++++++++++++++++++"

        header_len=len(report_header)
        terminal_width = shutil.get_terminal_size().columns
        padd=" "*abs((terminal_width-header_len)//2)

        print(padd+report_header)
        print(padd+f"{report_suc}" + abs(len(report_suc) - header_len+1) * " " + "|")
        print(padd+f"{report_refused}" + abs(len(report_refused) - header_len+1) * " " + "|")
        print(padd+f"{report_forced}" + abs(len(report_forced) - header_len+1) * " " + "|")
        print(padd+f"{report_black_listed}" + abs(len(report_black_listed) - header_len+1) * " " + "|")
        print(padd+f"{report_spam_protection}" + abs(len(report_spam_protection) - header_len+1) * " " + "|")
        print(padd+f"{_time}" + abs(len(_time) - header_len+1) * " " + "|")
        print(padd+report_footer)