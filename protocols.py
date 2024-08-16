from typing import Literal, Union, List, Optional, Any, Callable, Tuple

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PDFExtractConfig(BaseModel):
    # MinerU源码写的乱七八糟，不知道这个还能传啥
    modelList: List[str] = []
    maxSize: int = 10485760


class Config(BaseModel):
    pdfExtract: PDFExtractConfig


class PDFExtractRequest(BaseModel):
    # pdf的url，可以是http(s) url，也可以是data url
    # data url支持zstd过的文件，格式是data:application/pdf+zstd;base64,xxxxxx
    url: str
    # 模式，官方demo用的UNIPipe，我不知道有啥区别
    mode: Optional[Literal["uni", "text", "ocr"]] = "uni"
    # 输出的内容，默认全输出
    outputs: Optional[set[Literal["text", "markdown", "images"]]] = [
        "text",
        "markdown",
        "images",
    ]
    # 没实现，如果实现了大概长这样："some-bucket/path/to/some/dir"
    # 如果不传的话，在结果的images里
    imagesBucketPath: Optional[str] = None


class PDFExtractResponse(BaseModel):
    # uni模式生成的文本
    text: Optional[Any] = None
    # 生成的markdown
    markdown: Optional[Any] = None
    # 生成的图片，key是图片的path，
    # 当请求中imagesBucketPath未指定时：value是base64编码的图片dataurl
    # 否则为空串
    images: Optional[dict[str, str]] = None
