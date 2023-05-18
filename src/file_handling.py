import json, time, enum, pathlib
from typing import Any 

class File:
    class FileType(enum.Enum):
        UNKNOWN= "UNKNOWN"
        TXT= "text"
        HTML= "html"
        JSON= "json"
        PDF= "pdf"
        DOC= "doc"
        DOCX= "docx"

        @classmethod
        def _missing_(cls, value):
            return cls.UNKNOWN

    def __init__(self, path: str) -> None:
        if not File.is_file(path):
            raise FileNotFoundError(f"[ERROR] {path} does not exist!")
        self.path = path
        self.name = path.split("/")[-1]
        self.type = File.FileType(path.split(".")[-1].lower())

    def read_file(self, mode = None) -> bytes|str:
        if not mode:
            match self.type:
                case File.FileType.PDF | File.FileType.DOC | File.FileType.DOCX:
                    mode = "rb"
                case File.FileType.TXT | File.FileType.JSON | File.FileType.HTML:
                    mode = "r"
                case File.FileType.UNKNOWN:
                    raise Exception(f"Unknown file type! {self.path.split('.')[-1]}")
        
        with open(self.path, mode) as f:
            data = f.read()

        return data

    def readlines(self, mode = "r"):
        with open(self.path, mode) as f:
            lines = f.readlines()
        return lines

    def file_type(self) -> FileType:
        return self.type

    def file_path(self) -> str:
        return self.path
    
    def file_name(self) -> str:
        return self.name
    
    def write(self, data: Any, write_mode: str) -> None:
        with open(self.path, write_mode) as f:
            f.write(data)
 
    @staticmethod
    def is_file(path) -> bool:
        return pathlib.Path(path).is_file()

def get_timestamp(timestamp_path: str, email: str):
    ts_file = File(timestamp_path)
    ts_data: dict = json.loads(ts_file.read_file())
    if ts_data.get(email):
        print(f"{email}: {(time.time() - ts_data[email]) / 3600 :.2f} hrs. ago")
    else:
        print(f"{email}: Not Found!")


def load_timestamp(timestamp_path: str) -> dict[str, str]:
    return json.loads(File(timestamp_path).read_file())


def load_attachment(attachment_path: str, mode = None) -> dict[str, str|File.FileType|bytes]:
    f = File(attachment_path)
    return {
            "filename": f.file_name(),
            "path": attachment_path,
            "type": f.file_type(),
            "subtype": "octet-stream",
            "maintype": "application",
            "data": f.read_file(mode),
            }
