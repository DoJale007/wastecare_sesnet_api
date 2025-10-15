from enum import Enum
from fastapi import APIRouter, Form, status, HTTPException
from typing import Annotated
from pydantic import EmailStr
from db import users_collection, builders_collection, suppliers_collection
import bcrypt
import jwt
import os
from datetime import timezone, datetime, timedelta
from bson import ObjectId


class UserRole(str, Enum):
    USER = "user"
    SUPPLIER = "supplier"
    BUILDER = "builder"


# create users router
users_router = APIRouter(tags=["Users Routes- Registration/Login"])


# Define endpoints
@users_router.post("/users/register")
def register_user(
    email: Annotated[EmailStr, Form()],
    password: Annotated[str, Form(min_length=8)],
    username: Annotated[str, Form()],
    district: Annotated[str, Form()],
    phone: Annotated[str, Form()],
    role: Annotated[UserRole, Form()] = UserRole.USER,
    # Additional fields for builder role (optional in form, but required if role=BUILDER)
    company_name: Annotated[str | None, Form()] = None,
    builder_lead: Annotated[str | None, Form()] = None,
    # Additional fields for supplier role (optional in form, but required if role=SUPPLIER)
    shop_name: Annotated[str | None, Form()] = None,
    owner: Annotated[str | None, Form()] = None,
):
    # Ensure user does not exist
    user_count = users_collection.count_documents(filter={"email": email})
    if user_count > 0:
        raise HTTPException(status.HTTP_409_CONFLICT, "User already exist!")
    # Harsh user password
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    # Create a base user data
    user_doc = {
        "email": email,
        "password": hashed_password.decode(),
        "username": username,
        "district": district,
        "phone": phone,
        "role": role,
        "created_at": datetime.now(tz=timezone.utc),
    }
    # Insert user into users_collection in database
    result = users_collection.insert_one(user_doc)
    user_id = result.inserted_id
    # If user is a builder, save the additional builder data
    if role == UserRole.BUILDER:
        if not all([company_name, builder_lead]):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "Builder should Provide Company Name and Project Lead",
            )
        builders_collection.insert_one(
            {
                "user_id": ObjectId(user_id),
                "company_name": company_name,
                "builder_lead": builder_lead,
                "created_at": datetime.now(tz=timezone.utc),
            }
        )
    # If user is a supplier, save the additional supplier data
    if role == UserRole.SUPPLIER:
        if not all([shop_name, owner]):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "Supplier should Provide Shop Name and Owner",
            )
        suppliers_collection.insert_one(
            {
                "user_id": ObjectId(user_id),
                "shop_name": shop_name,
                "owner": owner,
                "created_at": datetime.now(tz=timezone.utc),
            }
        )
    # Return response
    return {"Message": f"{role.capitalize()}  registered successfully!"}


@users_router.post("/users/login")
def login_user(
    email: Annotated[EmailStr, Form()],
    password: Annotated[str, Form()],
):
    # Ensure user exist
    user = users_collection.find_one(filter={"email": email})
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User does not exist!")
    # Compare their password
    hashed_password_in_db = user["password"]
    correct_password = bcrypt.checkpw(password.encode(), hashed_password_in_db.encode())
    if not correct_password:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    # Generate an access token for them
    encoded_jwt = jwt.encode(
        {
            "id": str(user["_id"]),
            "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=60),
        },
        os.getenv("JWT_SECRET_KEY"),
        "HS256",
    )
    # Return response
    return {"Message": "User Logged in successfully!", "access_token": encoded_jwt}


# suppliers would possibly do an upload of absolute location and photo upload of their shop
# Checkout dropdown for Ghana Districts Attribute table---GIS
