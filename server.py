import logging
import os
import time
from typing import Any

from fastapi import FastAPI, HTTPException, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from magic_pdf.pipe.AbsPipe import AbsPipe
from magic_pdf.pipe.UNIPipe import UNIPipe
from magic_pdf.pipe.TXTPipe import TXTPipe
from magic_pdf.pipe.OCRPipe import OCRPipe

from pdf import MemoryReadWriter, fetchPDFUrl

from protocols import Config, PDFExtractRequest, PDFExtractResponse


# todo: load config from env/file
config = Config.model_validate_json(
    """
{
    "pdfExtract": {
        "maxSize": 10485760,
        "modelList": [
        ]
    }
}
"""
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/v1/pdf_extract")
async def pdf_extract(request: PDFExtractRequest, raw_request: Request):
    pdfBytes = await fetchPDFUrl(request.url)
    if len(pdfBytes) > config.pdfExtract.maxSize:
        raise HTTPException(
            status_code=413,
            detail=f"PDF too large: {len(pdfBytes)} greater than {config.pdfExtract.maxSize} bytes",
        )
    imageWriter = MemoryReadWriter()
    kw = {
        "pdf_bytes": pdfBytes,
        "image_writer": imageWriter,
        "is_debug": False,
    }
    pipe: AbsPipe
    if request.mode == "uni":
        pipe = UNIPipe(
            **kw,
            jso_useful_key={  # 不是typo，原文如此
                "_pdf_type": "",  # 不知道啥意思
                "model_list": config.pdfExtract.modelList,  # 不知道啥意思
            },
        )
    elif request.mode == "text":
        pipe = TXTPipe(**kw, model_list=config.pdfExtract.modelList)
    elif request.mode == "ocr":
        pipe = OCRPipe(**kw, model_list=config.pdfExtract.modelList)
    else:
        raise ValueError(f"Unsupported mode: {request.mode}")

    pipe.pipe_classify()
    pipe.pipe_analyze()
    pipe.pipe_parse()

    # TODO: 支持s3啥的
    imageParentPath = ""
    text = pipe.pipe_mk_uni_format(imageParentPath, drop_mode="none")
    markdown = pipe.pipe_mk_markdown(imageParentPath, drop_mode="none")
    return PDFExtractResponse(
        text="text" in request.outputs and text or None,
        markdown="markdown" in request.outputs and markdown or None,
        images="images" in request.outputs and imageWriter.dump() or None,
    )

@app.get("/v1/health")
async def health():
    return {"status": "ok"}

def mian():
    # start the server
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    mian()
