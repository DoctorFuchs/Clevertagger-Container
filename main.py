# uvicorn main:app

import codecs
import logging
from subprocess import Popen, PIPE
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from config import SMOR_MODEL

import clevertagger

clever = clevertagger.Clevertagger()

app = FastAPI()
logger = logging.getLogger("CleverTaggerLogger")


@app.post("/smor")
def get_smor(text: str):
    if not text or text.isspace():
        logger.error("no content delivered to get_tags")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST)
    try:
        process = Popen(["fst-infl2", SMOR_MODEL], stdin=PIPE, stdout=PIPE)
        stdout = process.communicate(input=text.encode("utf-8"))[0]

        return stdout.split()
    except Exception as e:
        logger.exception("get_smor threw exception: " + str(e))
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.post("/clever")
def get_tags(text: str):
    if not text or text.isspace():
        logger.error("no content delivered to get_tags")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST)
    try:
        return [word.split("\t") for word in clever.tag([text])[0].split("\n")]
    except Exception as e:
        logger.exception("get_tags threw exception: " + str(e))
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
