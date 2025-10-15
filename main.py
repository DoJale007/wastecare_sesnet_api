from fastapi import FastAPI
from routes.users import users_router


app = FastAPI()


@app.get("/")
def read_root():
    return {"Message": "Welcome to the WasteCare SESNET Web App"}


# Plugging routers into main.py
app.include_router(users_router)
