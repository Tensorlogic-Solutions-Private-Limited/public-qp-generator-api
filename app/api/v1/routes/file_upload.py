from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.data_upload_service import upload_excel_to_db, generate_excel_template
from app.api.v1.dependencies.auth import get_current_user
from app.models.user import User
import shutil
import os
from app.utils.get_user_role import get_user_role

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/v1/upload-excel", tags=["Bulk Upload"])
async def upload_excel(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload an Excel file to bulk insert questions into the database.

    - **Role Restriction**: Only users with admin role (role_code='100') can upload.
    - **File Format**: Must be `.xls` or `.xlsx`.
    - **Returns**: Success message if uploaded and processed.
    """
    # Fetch role explicitly using helper (to avoid lazy-loading errors)
    role_obj = await get_user_role(db, current_user.role_id)
    if not role_obj or role_obj.role_code != "100":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can upload Excel.")

    # Validate file type
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Invalid file format. Only Excel files are allowed.")

    # Save file to disk
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Process the file contents and insert into DB
    return await upload_excel_to_db(db, file_path)
@router.get("/v1/excel-template", tags=["Bulk Upload"])
async def download_question_excel_template(
    current_user: User = Depends(get_current_user)  
):
    """
    Authenticated endpoint to download Excel question template.
    """
    return generate_excel_template()