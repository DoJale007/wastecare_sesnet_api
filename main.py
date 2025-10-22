from fastapi import FastAPI
from routes.users import users_router
from routes.public import public_router
from routes.enterprises import enterprises_router
from routes.admin import admin_router
import cloudinary
import os
from dotenv import load_dotenv

load_dotenv()

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)


app = FastAPI(
    title="Sustainable Enterprise-Solutions Network Africa Web App(SESNET-Africa)",
    description="A comprehensive digital platform that connects sanitation enterprises, customers, and administrators to promote sustainable waste management across Africa.",
    version="1.0.0",
    contact={
        "name": "SESNET-Africa Development Team",
        "email": "enquiries@sesnet-africa.com",
        "url": "https://sesnet-africa.com",
    },
)


@app.get("/")
def read_root():
    return {"Message": "Welcome to the WasteCare SESNET Web App"}


# Plugging routers into main.py
app.include_router(users_router)
app.include_router(admin_router)
app.include_router(enterprises_router)
app.include_router(public_router)
