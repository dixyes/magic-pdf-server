import base64
from typing import Union
import urllib.parse
import zstd
import aiohttp
from magic_pdf.rw.AbsReaderWriter import AbsReaderWriter


def parseDataURL(url: str) -> bytes:
    info, data = url.removeprefix("data:").split(",", 1)
    mimeEncoding = info.split(";", 1)
    if len(mimeEncoding) == 1:
        mime = mimeEncoding[0]
        encoding = None
    else:
        mime, encoding = mimeEncoding
    if encoding and encoding != "base64":
        raise ValueError(f"Unsupported encoding: {encoding}")

    compression = None
    if mime == "application/pdf":
        pass
    elif mime == "application/pdf+zstd":
        compression = "zstd"
    else:
        raise ValueError(f"Unsupported MIME type: {mime}")

    ret: bytes
    if encoding == "base64":
        ret = base64.b64decode(data)
    elif encoding is None:
        ret = urllib.parse.unquote(data).encode("utf-8")

    if compression == "zstd":
        ret = zstd.ZSTD_uncompress(ret)

    return ret


async def fetchPDFUrl(url: str) -> bytes:
    if url.startswith("data:"):
        # is a data url, parse it
        return parseDataURL(url)
    elif url.startswith("http") or url.startswith("https"):
        # is a url, fetch it
        return await aiohttp.request("GET", url)
    else:
        raise ValueError("Unsupported URL type")


# TODO: 整一个文件服务/s3 rw
class MemoryReadWriter(AbsReaderWriter):
    MODE_TXT = "text"
    MODE_BIN = "binary"
    files: dict[str, bytes]

    def __init__(self):
        self.files = {}

    def read(self, path: str, mode=MODE_TXT) -> Union[bytes, str]:
        if path not in self.files:
            raise FileNotFoundError(f"File not found: {path}")
        if mode == self.MODE_TXT:
            return self.files[path].decode("utf-8")
        else:
            return self.files[path]

    def write(self, content: Union[bytes, str], path: str, mode=MODE_TXT):
        if mode == self.MODE_TXT:
            if not isinstance(content, bytes):
                raise ValueError("Content must be bytes when mode is text")
            self.files[path] = content.encode("utf-8")
        else:
            if not isinstance(content, bytes):
                raise ValueError("Content must be bytes when mode is binary")
            self.files[path] = content

    def read_offset(self, path: str, offset=0, limit=None) -> Union[bytes, str]:
        if path not in self.files:
            raise FileNotFoundError(f"File not found: {path}")
        if limit is None:
            return self.files[path][offset:]
        else:
            return self.files[path][offset : offset + limit]

    def dump(self) -> dict[str, str]:
        ret = {}
        for path, content in self.files.items():
            mime: str
            if path.endswith(".png"):
                mime = "image/png"
            elif path.endswith(".jpg") or path.endswith(".jpeg"):
                mime = "image/jpeg"
            elif path.endswith(".svg"):
                mime = "image/svg+xml"
            elif path.endswith(".tif") or path.endswith(".tiff"):
                mime = "image/tiff"
            elif path.endswith(".bmp"):
                mime = "image/bmp"
            elif path.endswith(".avif"):
                mime = "image/avif"
            elif path.endswith(".webp"):
                mime = "image/webp"
            elif path.endswith(".ico"):
                mime = "image/vnd.microsoft.icon"
            elif path.endswith(".heic") or path.endswith(".heif"):
                mime = "image/heif"

            ret[path] = (
                "data:" + mime + ";base64," + base64.b64encode(content).decode("utf-8")
            )
        return ret
