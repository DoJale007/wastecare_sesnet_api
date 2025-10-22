from enum import Enum
from fastapi import APIRouter, Form, File, UploadFile, status, HTTPException
from typing import Annotated, Optional
from pydantic import EmailStr
from db import users_collection, enterprises_collection
import bcrypt
import jwt
from dotenv import load_dotenv
import os
import cloudinary
import cloudinary.uploader
from datetime import timezone, datetime, timedelta
from bson import ObjectId

load_dotenv()

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)


class UserRole(str, Enum):
    ADMIN = "admin"
    ENTERPRISE = "enterprise"
    CUSTOMER = "customer"


users_router = APIRouter(tags=["Users Routes - Registration & Login"])


@users_router.post("/users/register")
def register_user(
    email: Annotated[EmailStr, Form()],
    password: Annotated[str, Form(min_length=8)],
    username: Annotated[str, Form()],
    phone: Annotated[str, Form()],
    district: Annotated[str, Form()],
    role: Annotated[UserRole, Form()] = UserRole.CUSTOMER,
    flyer: Optional[UploadFile] = File(None),
    digital_address: Optional[str] = Form(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    description: Optional[str] = Form(None),
):
    # Ensure user does not exist
    if users_collection.find_one({"email": email}):
        raise HTTPException(status.HTTP_409_CONFLICT, "User already exists!")

    # Hash password properly
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    # Base user record
    user_doc = {
        "email": email,
        "password": hashed_password,
        "username": username,
        "phone": phone,
        "district": district,
        "role": role,
        "created_at": datetime.now(tz=timezone.utc),
    }

    result = users_collection.insert_one(user_doc)
    user_id = result.inserted_id

    # If enterprise, store additional info
    if role == UserRole.ENTERPRISE:
        missing_fields = []
        if not flyer:
            missing_fields.append("flyer")
        if not digital_address:
            missing_fields.append("digital_address")
        if not latitude or not longitude:
            missing_fields.append("GPS coordinates")
        if not description:
            missing_fields.append("description")

        if missing_fields:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"Enterprise missing required fields: {', '.join(missing_fields)}",
            )

        try:
            upload_result = cloudinary.uploader.upload(flyer.file)
        except Exception as exp:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Image upload failed: {str(exp)}",
            )

        enterprises_collection.insert_one(
            {
                "user_id": ObjectId(user_id),
                "enterprise_name": username,
                "flyer": upload_result["secure_url"],
                "digital_address": digital_address,
                "gps_location": {"lat": latitude, "lon": longitude},
                "description": description,
                "approved": False,
                "created_at": datetime.now(tz=timezone.utc),
            }
        )

    return {
        "Message": f"{role.capitalize()} registered successfully!",
        "user_id": str(user_id),
        "role": role,
    }


@users_router.post("/users/login")
def login_user(email: Annotated[EmailStr, Form()], password: Annotated[str, Form()]):
    user = users_collection.find_one({"email": email})
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found!")

    hashed_password_in_db = user["password"]
    if not bcrypt.checkpw(password.encode(), hashed_password_in_db.encode()):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid login credentials")

    token_payload = {
        "id": str(user["_id"]),
        "role": user["role"],
        "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=120),
    }
    encoded_jwt = jwt.encode(token_payload, os.getenv("JWT_SECRET_KEY"), "HS256")

    return {
        "Message": "User logged in successfully!",
        "access_token": encoded_jwt,
        "role": user["role"],
        "user_id": str(user["_id"]),
    }
