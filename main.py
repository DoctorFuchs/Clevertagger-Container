#uvicorn main:app

import codecs
import logging
import subprocess
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

import clevertagger

clever = clevertagger.Clevertagger()

app = FastAPI()
logger = logging.getLogger('CleverTaggerLogger')

@app.post("/smor")
def get_smor(text: str):
    if not text or text.isspace():
        logger.error('no content delivered to get_tags')
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST)
    try:
        subprocess.run("echo '" + text + "' | fst-infl2 ../../data/zmorge/zmorge-20150315-smor_newlemma.ca > /clevertagger/clevertagger/test.txt", shell=True)
        with codecs.open('test.txt', 'rb', 'utf8') as f:
            return f.readlines()
    except Exception as e:
        logger.exception('get_smor threw exception: ' + str(e))
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@app.post("/clever")
def get_tags(text: str):
    if not text or text.isspace():
        logger.error('no content delivered to get_tags')
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST)
    try:
        return clever.tag([text])
    except Exception as e:
        logger.exception('get_tags threw exception: ' + str(e))
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)