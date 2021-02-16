#uvicorn main:app

import logging
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

#import clevertagger

#clever = clevertagger.Clevertagger()

app = FastAPI()
logger = logging.getLogger('CleverTaggerLogger')

@app.post("/smor")
def get_smor():
    pass

@app.post("/clever")
def get_tags(text: str):
    pass
    """
    if not text or text.isspace():
        logger.error('no content delivered to get_tags')
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST)
    try:
        return tagger.tag(text)
    except Exception as e:
        logger.exception('get_tags threw exception: ' + str(e))
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    """