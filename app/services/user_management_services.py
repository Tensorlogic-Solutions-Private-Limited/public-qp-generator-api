from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from app.models. user import User
from fastapi import HTTPException, status
from sqlalchemy.orm import joinedload
from app.models.user import User, Role
from app.utils.get_user_role import get_user_role
from app.utils.auth import get_password_hash
from app.schemas.auth import UserUpdateRequest

async def list_users_service(db: AsyncSession, skip: int, limit: int):
    query = (
        select(User)
        .options(joinedload(User.role))
        .where(User.is_active == True)
        .order_by(User.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    return result.scalars().all()

async def count_active_users(db: AsyncSession):
    result = await db.execute(select(User).where(User.is_active == True))
    return len(result.scalars().all())

async def update_user_service(
    db: AsyncSession,
    user_id: int,
    new_password: str,
    current_user: User
):
    # Fetch target user
    result = await db.execute(select(User).where(User.id == user_id))
    target_user = result.scalar_one_or_none()
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Check role of current user
    role_obj = await get_user_role(db, current_user.role_id)
    is_admin = role_obj.role_code == "100"

    # Only allow user to change their own password, or admin
    if not is_admin and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this password")

    # Update and save password
    target_user.hashed_password = get_password_hash(new_password)
    await db.commit()

    return {"message": f"Password updated successfully for user: {target_user.username}"}

async def get_user_by_id_service(user_id: int, db: AsyncSession) -> User:
    result = await db.execute(
        select(User).where(User.id == user_id).options(joinedload(User.role))
    )
    user_obj = result.scalar_one_or_none()

    if not user_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user_obj

async def update_user_info_service(
    db: AsyncSession,
    user_id: int,
    username: str,
    role_code: str,
    is_active: bool,
    current_user: User
):
    # Check if current user is admin
    current_user_role = await get_user_role(db, current_user.role_id)
    if current_user_role.role_code != "100":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins only")

    # Fetch target user
    result = await db.execute(select(User).where(User.id == user_id))
    target_user = result.scalar_one_or_none()
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Fetch role_id from role_code
    role_result = await db.execute(select(Role).where(Role.role_code == role_code))
    role_obj = role_result.scalar_one_or_none()
    if not role_obj:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role code")

    # Update user details
    target_user.username = username
    target_user.role_id = role_obj.id
    target_user.is_active = is_active

    await db.commit()
    await db.refresh(target_user)

    return {"message": f"User '{username}' updated successfully."}