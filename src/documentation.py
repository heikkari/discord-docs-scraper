from io import BytesIO
from zipfile import ZipFile
from typing import Dict
import requests


def download(github_repository: str) -> bytes:
    url = "https://codeload.github.com/{}/zip/refs/heads/master".format(github_repository)
    return requests.get(url).content

def get(zip_archive: bytes) -> Dict[str, str]:
    """
        returns { file_path: content }
    """

    pages = {}
    file = BytesIO(zip_archive)

    with ZipFile(file, "r") as zip:
        files = [zip_info for zip_info in zip.infolist() if "/docs/" in zip_info.filename]

        for file in files:
            if not file.filename.endswith(".md"):
                continue

            with zip.open(file.filename, "r") as f:
                pages[file.filename] = f.read()

    return pages

