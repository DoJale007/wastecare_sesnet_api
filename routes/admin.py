from fastapi import APIRouter, HTTPException, status, Form, Depends
from bson import ObjectId
from datetime import datetime, timezone
from db import enterprises_collection, users_collection
from dependencies.authz import has_roles, UserRole
from utils import replace_mongo_id


# Admin routerconfiguration
admin_router = APIRouter(
    prefix="/admin",
    tags=["Admin Access"],
    dependencies=[Depends(has_roles([UserRole.ADMIN]))],
)


# View all pending enterprises
@admin_router.get("/enterprises/pending")
def view_pending_enterprises():
    enterprises = list(enterprises_collection.find({"approved": {"$ne": True}}))
    formatted_list = [replace_mongo_id(enterprise) for enterprise in enterprises]
    return {"count": len(formatted_list), "data": formatted_list}


# Approve or reject an enterprise
@admin_router.patch("/enterprises/{enterprise_id}/approval")
def approve_enterprise(enterprise_id: str, approved: bool = Form(...)):
    update_result = enterprises_collection.update_one(
        {"_id": ObjectId(enterprise_id)},
        {"$set": {"approved": approved, "updated_at": datetime.now(tz=timezone.utc)}},
    )

    if update_result.matched_count == 0:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Enterprise not found.")

    action = "approved" if approved else "rejected"
    return {"message": f"Enterprise {action} successfully."}


# Delete an enterprise
@admin_router.delete("/enterprises/{enterprise_id}")
def delete_enterprise(enterprise_id: str):
    result = enterprises_collection.delete_one({"_id": ObjectId(enterprise_id)})
    if result.deleted_count == 0:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Enterprise not found.")
    return {"message": "Enterprise deleted successfully."}


#  View all registred users plus enterprise info
@admin_router.get("/users")
def get_all_users():
    users_data = []

    users = users_collection.find()
    for user in users:
        user_data = replace_mongo_id(user)

        # If user is an enterprise, fetch enterprise details
        if user_data.get("role") == "enterprise":
            enterprise = enterprises_collection.find_one(
                {"user_id": ObjectId(user_data["id"])}
            )
            if enterprise:
                user_data["enterprise_info"] = replace_mongo_id(enterprise)
            else:
                user_data["enterprise_info"] = None
        else:
            user_data["enterprise_info"] = None

        users_data.append(user_data)

    return {"count": len(users_data), "data": users_data}
