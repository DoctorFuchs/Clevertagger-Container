# uvicorn main:app

import re
import logging
from typing import List, Tuple
from subprocess import Popen, PIPE
from pydantic import BaseModel, Field
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST

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


class LemmaResponse(BaseModel):
    query: str = Field(..., example="cleverer")
    results: str = Field(..., example="clever")

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
        logger.error("no content delivered to get_smor")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST)

    try:
        process = Popen(["fst-infl2", SMOR_MODEL], stdin=PIPE, stdout=PIPE)
        stdout = process.communicate(input=text.encode("utf-8"))[0]

        return {"query": text, "results": stdout.split()}
    except Exception as e:
        logger.exception("get_smor threw exception: " + str(e))
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

"""
>
Führungszeugnisse
Führ<~>ungs<#>zeug<#>nisse<+NN><Fem><Acc><Sg>
Führ<~>ungs<#>zeug<#>nisse<+NN><Fem><Dat><Sg>
Führ<~>ungs<#>zeug<#>nisse<+NN><Fem><Gen><Sg>
Führ<~>ungs<#>zeug<#>nisse<+NN><Fem><Nom><Sg>
Führ<~>ungs<#>zeugnis<+NN><Neut><Dat><Sg><Old>
Führ<~>ungs<#>zeugnis<+NN><Neut><Acc><Pl>
Führ<~>ungs<#>zeugnis<+NN><Neut><Gen><Pl>
Führ<~>ungs<#>zeugnis<+NN><Neut><Nom><Pl>
Führung<->s<#>zeug<#>nisse<+NN><Fem><Acc><Sg>
Führung<->s<#>zeug<#>nisse<+NN><Fem><Dat><Sg>
Führung<->s<#>zeug<#>nisse<+NN><Fem><Gen><Sg>
Führung<->s<#>zeug<#>nisse<+NN><Fem><Nom><Sg>
Führung<->s<#>zeugnis<+NN><Neut><Dat><Sg><Old>
Führung<->s<#>zeugnis<+NN><Neut><Acc><Pl>
Führung<->s<#>zeugnis<+NN><Neut><Gen><Pl>
Führung<->s<#>zeugnis<+NN><Neut><Nom><Pl>
"""
@app.post("/lemma", response_model=LemmaResponse)
def get_lemma(req: SmorRequest):
    text = req.text

    if not text or text.isspace():
        logger.error("no content delivered to get_lemma")
        return JSONResponse(status_code=status-HTTP_400_BAD_REQUEST)

    try:
        process = Popen(["fst-infl2", SMOR_MODEL], stdin=PIPE, stdout=PIPE)
        stdout = process.communicate(input=text.encode("utf-8"))[0]
        #remove morpheme markers
        stdout = re.sub(r'(<->|<~>|<#>)', '', stdout.decode("utf-8"))
        #split by the various analyses
        hypotheses = stdout.split()
        #remove all the markup that we don't need
        hypotheses = list(filter(lambda y: '>' not in y, (map(lambda x: re.sub(r'<.*[A-Z].*>', '', x), [h for h in hypotheses]))))
        #we return the shortest string since we think it's the lemma
        return {"query": text, "results": sorted(hypotheses, key=len)[0]}
    except Exception as e:
        logger.exception("get_lemma threw exception: " + str(e))
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
