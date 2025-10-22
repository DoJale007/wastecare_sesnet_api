# routes/enterprises.py
from fastapi import APIRouter, HTTPException, status, Form, File, UploadFile, Depends
from bson import ObjectId
from db import enterprises_collection
from datetime import datetime, timezone
import cloudinary.uploader
from dependencies.authn import authenticated_user
from dependencies.authz import has_roles, UserRole

enterprises_router = APIRouter(
    tags=["Enterprise Access"], dependencies=[Depends(has_roles([UserRole.ENTERPRISE]))]
)


# Update own enterprise profile
@enterprises_router.put("/enterprises/update/{enterprise_id}")
def update_enterprise_profile(
    enterprise_id: str,
    auth_user: dict = Depends(authenticated_user),
    description: str = Form(None),
    digital_address: str = Form(None),
    latitude: float = Form(None),
    longitude: float = Form(None),
    flyer: UploadFile = File(None),
):
    enterprise = enterprises_collection.find_one({"_id": ObjectId(enterprise_id)})
    if not enterprise:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Enterprise not found.")

    # Check ownership
    if str(enterprise["user_id"]) != str(auth_user["id"]):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "Not authorized to edit this enterprise."
        )

    update_data = {}
    if description:
        update_data["description"] = description
    if digital_address:
        update_data["digital_address"] = digital_address
    if latitude and longitude:
        update_data["gps_location"] = {"lat": latitude, "lon": longitude}
    if flyer:
        upload_result = cloudinary.uploader.upload(flyer.file)
        update_data["flyer"] = upload_result["secure_url"]

    if not update_data:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No update data provided.")

    update_data["updated_at"] = datetime.now(tz=timezone.utc)
    enterprises_collection.update_one(
        {"_id": ObjectId(enterprise_id)},
        {"$set": update_data},
    )

    return {"message": "Enterprise profile updated successfully."}
