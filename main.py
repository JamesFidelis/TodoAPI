import fastapi
import uvicorn

api = fastapi.FastAPI()

@api.get('/')
async def  hello():
    return {
        "Message": "Hello There!"
    }

uvicorn.run(api)