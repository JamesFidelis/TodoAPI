from fastapi import FastAPI, Depends
import models
from database import engine
from routers import auth, todos, companyapis, dependencies

app = FastAPI()
models.Base.metadata.create_all(bind=engine)


app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(companyapis.router,
                   prefix="/company",
                   tags=["company"],
                   dependencies=[Depends(dependencies.get_token_header)]
                   )
