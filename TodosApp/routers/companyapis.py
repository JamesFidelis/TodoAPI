from fastapi import APIRouter


router = APIRouter()



@router.get("/name")
async def get_company_name():
    return {'name': 'comapny name xample '}

