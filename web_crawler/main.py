from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl
import requests
from bs4 import BeautifulSoup


app = FastAPI()

class UrlTarget(BaseModel):
    url: HttpUrl


@app.get('/')
async def index():
    msg = 'hi guys, it is a simple web crawler with fastapi, plaese go to address (/web_crawler)'
    return JSONResponse(status_code=200, content=msg)


@app.get('/web_crawler')
async def crawler(url:UrlTarget=Depends()):
    page = requests.get(str(url.url))

    if page.status_code == 200:
        soup = BeautifulSoup(page.text, 'html.parser')

        def get_title():
            return soup.head.find('title').text if soup.head.find('title') else None

        def get_description():
            return soup.head.find('meta', attrs={'name':'description'}).get(
                'content') if soup.head.find('meta', attrs={'name':'description'}) else None

        def get_keywords():
            return soup.head.find('meta', attrs={'name':'keywords'}).get(
                'content') if soup.head.find('meta', attrs={'name':'keywords'}) else None
        
        def get_image():
            return soup.head.find('meta', attrs={'name':'image'}).get(
                'content') if soup.head.find('meta', attrs={'name':'image'}) else None

        return {
            "title":get_title(),
            "description":get_description(),
            "keywords":get_keywords(),
            "image":get_image(),
        }

    else:
        return JSONResponse(status_code=page.status_code, content='please check your URL')