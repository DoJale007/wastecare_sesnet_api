from fastapi import APIRouter, HTTPException, status
from bson import ObjectId
from db import enterprises_collection

public_router = APIRouter(tags=["Public Access"])


# Get all approved enterprises (Purchaser’s Guide)
@public_router.get("/enterprises/")
def get_all_approved_enterprises():
    enterprises = list(enterprises_collection.find({"approved": True}))
    if not enterprises:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No approved enterprises found.")

    for e in enterprises:
        e["id"] = str(e["_id"])
        del e["_id"]
        if "user_id" in e:
            e["user_id"] = str(e["user_id"])
    return {"count": len(enterprises), "data": enterprises}


# Get a single enterprise by ID
@public_router.get("/enterprises/{enterprise_id}")
def get_enterprise_by_id(enterprise_id: str):
    enterprise = enterprises_collection.find_one(
        {"_id": ObjectId(enterprise_id), "approved": True}
    )
    if not enterprise:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, "Enterprise not found or not approved."
        )

    enterprise["id"] = str(enterprise["_id"])
    del enterprise["_id"]
    if "user_id" in enterprise:
        enterprise["user_id"] = str(enterprise["user_id"])
    return enterprise
