from pydantic import BaseModel
from pydantic.dataclasses import dataclass
from dataclasses import asdict
from typing import List
from datetime import datetime
from email.message import EmailMessage
from email.headerregistry import Address
import re
from consts import *

from file_handling import *


@dataclass
class Attachment:
    filename: str
    path: str
    type: File.FileType
    subtype: str
    maintype: str
    data: bytes = None

    def __post_init__(self) -> None:
        if not self.data: self.data = File(self.path).read_file("rb")

    def to_dict(self) -> dict[str, str]:
        return {k:v for k,v in  asdict(self).items() if k in ["filename", "subtype", "maintype"]}


@dataclass
class EmailMessageContents:
    sender_email: str
    subject: str
    sender_name: str | None = None
    attachments: List[Attachment] | None = None
    body_tokens: List[str] | None = None
    body: str | None = None
    body_format: File.FileType | None = None

    def __post_init__(self) -> None:
        self.set_body(self.body)

    def set_body(self, body: str) -> None:
        self.body, self.body_format = load_body(body)
        self.body_tokens = self.get_tokens()
    
    def has_tokens(self) -> bool:
        return bool(self.body_tokens)

    def get_tokens(self, remove_duplicate=False) -> list[str]:
        tokens = [match.group() for match in re.finditer(TOKEN_PATTERN, self.body)]
        if remove_duplicate: return list(set(tokens))
        return tokens
    
    def token_count(self) -> int:
        return len(self.get_tokens())

    def get_unique_tokens(self) -> list[str]:
        return list(set(self.get_tokens()))

    def unique_tokens_count(self) -> int:
        return len(list(set(self.get_tokens())))

    def replace_tokens(self, replacement: dict[str, str]) -> None:
        if not self.has_tokens(): raise Exception("email body doesn't has and tokens.")
        if self.unique_tokens_count() != len(replacement.keys()):
            raise Exception(f"""\n{R}{len(replacement.keys())} tokens provided: {replacement}
                                while email body has {self.unique_tokens_count()} tokens: {self.get_unique_tokens()}{W}""")
        self.body = re.sub(TOKEN_PATTERN, lambda match: replacement[match.group()], self.body)
    
    def construct_email_message(self, to_email: str | None = None, to_name: str | None = None) -> EmailMessage:
        msg = EmailMessage()
        msg['subject'] = self.subject
        msg['From'] = Address(self.sender_name, *self.sender_email.split('@'))
        if to_email:
            msg['To'] = Address(to_name if to_name else to_email, *to_email.split("@"))

        if self.body_format == File.FileType.TXT: 
            msg.set_content(self.body)
        elif self.body_format == File.FileType.HTML: 
            msg.set_content(self.body, subtype=File.FileType.HTML.value)
        else:
            msg.set_content(bytes(self.body, 'utf-8').decode('unicode_escape'))

        if self.attachments:
            for att in self.attachments:
                msg.add_attachment(att.data, **att.to_dict())
        
        return msg


class AccountConfig(BaseModel):
    SMTP_server: str
    port: int
    email: str
    password: str
    timeout: int = 400


class EasyMailSettings(BaseModel):
    spam_protection_period:int
    allow_duplicate: bool
    force_sending: bool
    delivery_report: bool


def delta_time_hrs(time: str) -> float:
    now = datetime.now()
    ts = datetime.strptime(time, DATE_TIME_FORMAT)
    return abs((now - ts).total_seconds() / 3600)


def update_timestamp(timestamp_path: str, email: str) -> None:
    ts_file = File(timestamp_path.strip().strip("\n"))
    ts_data = json.loads(ts_file.read_file())
    ts_data[email] = datetime.now().strftime(DATE_TIME_FORMAT)
    ts_file.write(json.dumps(ts_data), "w")


def load_config(config_path: str) -> tuple[AccountConfig, EmailMessageContents, EasyMailSettings]:
    config = json.loads(File(config_path.strip().strip("\n")).read_file())
    return (
        AccountConfig(**config["account"]), 
        EmailMessageContents(sender_email=config["account"]["email"], **config["email_message_contents"]), 
        EasyMailSettings(**config["easymail_settings"])
    )
