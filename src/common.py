
from pydantic import validate_arguments
from dataclasses import dataclass, field, asdict
from typing import Any, List
from datetime import datetime

from file_handling import *

# consts
R = "\033[91m"  # red
G = "\033[92m"  # green
C = "\033[96m"  # cyan
Y = "\033[93m"  # yellow
W = "\033[00m"  # white
UL = "\033[4m"  # under line
DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

@dataclass
class Attachment:
    filename: str
    path: str
    type: File.FileType
    subtype: str
    maintype: str
    data: bytes = field(default=None)

    def __post_init__(self):
        if data:= isinstance(File(self.path).read_file(), bytes): self.data = data

    def to_dict(self):
        return {k:v for k,v in  asdict(self).items() if k in ["filename", "subtype", "maintype"]}


@validate_arguments
@dataclass
class EmailMessageContents:
    sender_name: str
    subject: str
    body_path: str
    attachments: List[Attachment]
    body: str = field(default=None)

    def __post_init__(self):
        if File.is_file(self.body_path): 
            self.body = File(self.body_path).read_file("r")
        else:
            raise FileNotFoundError(f"{self.body_path} was not found.")

    def change_body_path(self, body_path: str):
        if File.is_file(body_path): 
            self.body_path = body_path.strip().strip("\n")
            self.body = File(self.body_path).read_file("r").strip().strip("\n")
        else:
            raise FileNotFoundError(f"{body_path} was not found.")

    def format_body(self, *args):
        if "{}" not in self.body: raise Exception("email body cannot be formatted.")
        if self.body.count("{}") > len(args): raise IndexError(f"Replacement index {self.body.count('{}') - 1} out of range for positional args tuple")
        if self.body.count("{}") < len(args): raise IndexError(f"positional args index {len(args) - 1} out of range for replacement")
        self.body = self.body.format(*args)    


@validate_arguments
@dataclass
class AccountConfig:
    SMTP_server: str
    port: int
    email: str
    password: str
    timeout: int = field(default=400)


@validate_arguments
@dataclass
class EasyMailSettings:
    spam_protection_period:int
    allow_duplicate: bool
    force_sending: bool
    delivery_report: bool

def delta_time_hrs(time: str) -> float:
    now = datetime.now()
    ts = datetime.strptime(time, DATE_TIME_FORMAT)
    return abs((now - ts).total_seconds() / 3600)

def update_timestamp(timestamp_path: str, email: str):
    ts_file = File(timestamp_path.strip().strip("\n"))
    ts_data = json.loads(ts_file.read_file())
    ts_data[email] = datetime.now().strftime(DATE_TIME_FORMAT)
    ts_file.write(json.dumps(ts_data), "w")

def load_config(config_path: str) -> tuple[AccountConfig, EmailMessageContents, EasyMailSettings]:
    config = json.loads(File(config_path.strip().strip("\n")).read_file())
    return AccountConfig(**config["email_account"]), EmailMessageContents(**config["email_message_contents"]), EasyMailSettings(**config["easymail_settings"])
