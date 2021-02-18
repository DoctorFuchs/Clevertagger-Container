# uvicorn main:app

import codecs
import logging
from typing import List, Tuple
from subprocess import Popen, PIPE
from pydantic import BaseModel, Field
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from config import SMOR_MODEL

import clevertagger

clever = clevertagger.Clevertagger()

app = FastAPI()
logger = logging.getLogger("CleverTaggerLogger")


class SmorResponse(BaseModel):
    query: str = Field(..., example="cleverer")
    results: List[str] = Field(
        ...,
        example=[
            ">",
            "cleverer",
            "clever<+ADJ><Pos><NoGend><Gen><Pl><St>",
            "clever<+ADJ><Pos><Fem><Dat><Sg><St>",
            "clever<+ADJ><Pos><Fem><Gen><Sg><St>",
            "clever<+ADJ><Pos><Masc><Nom><Sg><St>",
            "clever<+ADJ><Comp><Adv>",
            "clever<+ADJ><Comp><Pred>",
        ],
    )


class CleverResponse(BaseModel):
    query: str = Field(..., example="ein toller Text")
    results: List[Tuple[str, str]] = Field(
        ...,
        example=[
            ("ein", "ART"),
            ("toller", "ADJA"),
            ("Text", "NN"),
        ],
    )


class SmorRequest(BaseModel):
    text: str = Field(..., example="cleverer")


class CleverRequest(BaseModel):
    text: str = Field(..., example="ein toller Text")


@app.post("/smor", response_model=SmorResponse)
def get_smor(req: SmorRequest):
    text = req.text

    if not text or text.isspace():
        logger.error("no content delivered to get_tags")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST)

    try:
        process = Popen(["fst-infl2", SMOR_MODEL], stdin=PIPE, stdout=PIPE)
        stdout = process.communicate(input=text.encode("utf-8"))[0]

        return {"query": text, "results": stdout.split()}
    except Exception as e:
        logger.exception("get_smor threw exception: " + str(e))
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.post("/clever", response_model=CleverResponse)
def get_tags(req: CleverRequest):
    text = req.text

    if not text or text.isspace():
        logger.error("no content delivered to get_tags")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST)

    try:
        return {
            "query": text,
            "results": [
                tuple(word.split("\t")) for word in clever.tag([text])[0].split("\n")
            ],
        }
    except Exception as e:
        logger.exception("get_tags threw exception: " + str(e))
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
