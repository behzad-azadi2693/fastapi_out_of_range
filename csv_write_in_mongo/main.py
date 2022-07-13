from fastapi import FastAPI, File, UploadFile, BackgroundTasks, Depends, HTTPException, Body, Path
import motor.motor_asyncio
from fastapi.responses import JSONResponse
from pydantic import BaseModel, validator
import pandas as pd
from fastapi.encoders import jsonable_encoder


engine = 'mongodb://user:password@localhost:27017'

connection = motor.motor_asyncio.AsyncIOMotorClient(engine)

db = connection['csv_db']


app = FastAPI()



class CsvFile(BaseModel):
    collection_name: str = Body(...)
    my_file: UploadFile = File(...)

    @validator('my_file')
    def check_my_file(cls, v, **kwargs):
        if not v.content_type in ['text/csv']:
            return HTTPException(status_code=400, detail='file must be csv')
        
        return v



async def save_csv_to_mongo(coll_name, my_file):
    collection = db[coll_name]
    datas = pd.read_csv(my_file.file, delimiter=";")
    convert_datas = datas.to_dict(orient="records")
    '''
    create_list = []
    
    length = len(list(convert_datas[0].keys())[0].split(';'))

    for data in convert_datas:
        dictionary = {}

        for i in range(length):
            dictionary[f"{list(convert_datas[0].keys())[0].split(';')[i]}"] = f"{list(convert_datas[0].values())[0].split(';')[i]}"
            #print(f"{list(convert_datas[0].keys())[0].split(';')[i]}")
            #print(f"{list(convert_datas[0].values())[0].split(';')[i]}")
        create_list.append(dictionary)
    '''
    await collection.insert_many(jsonable_encoder(create_list))



@app.get('/')
async def index():
    msg = 'this for save file csv in mongo db got to (/save_csv)'

    return JSONResponse(status_code=200, content=msg)



@app.post('/save_csv')
async def csv_saave(backgroundtask:BackgroundTasks, csv_file:CsvFile=Depends()):
    backgroundtask.add_task(save_csv_to_mongo, csv_file.collection_name, csv_file.my_file)

    return JSONResponse(status_code=200, content='csv is saving in mongo in background')



@app.get('/check/{collection_name:str}')
async def check(collection_name:str = Path()):
    collection = db[collection_name]
    books = []
    
    async for book in collection.find({}, {'_id': False}):
        books.append(book)

    return books
