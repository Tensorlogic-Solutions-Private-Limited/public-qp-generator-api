from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional, Union
from app.database import get_db
from app.models import master, user
from app.schemas.auth import (UserCreate, LoginRequest, 
                              LoginResponse, RoleListResponse,RoleResponse, 
                              UserResponse, PasswordUpdateRequest,UserUpdateRequest)
from app.utils import auth
from sqlalchemy.orm import joinedload
from app.services.user_management_services import (list_users_service, count_active_users, 
                                                   update_user_service, get_user_by_id_service,
                                                   update_user_info_service)
from app.utils.get_user_role import get_user_role
from app.utils.auth import get_current_user

router = APIRouter()

@router.post("/v1/register", tags=["User Management"])
async def register(
    request: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Register a new user.

    ### Request Headers:
    - `Content-Type`: application/json
    - *(Optional)* `Authorization`: Bearer token (if restricted to certain users)

    ### Path Parameters:
    - None

    ### Query Parameters:
    - None

    ### Request Body (application/json):
    - **username** (str): The desired username for the new user.
    - **password** (str): The user's password (will be securely hashed).
    - **role_code** (str or int): The role code to assign to the user.
        - `100`: admin
        - `101`: teacher

    Example:
    ```json
    {
        "username": "john_doe",
        "password": "securePassword123",
        "role_code": "101"
    }
    ```

    ### Response (application/json):
    - **201 Created** (if successful)
    ```json
    {
        "message": "User created successfully"
    }
    ```

    ### Error Responses:
    - **400 Bad Request**
        - If the username already exists:
        ```json
        {
            "detail": "Username already exists"
        }
        ```
        - If the role code is invalid:
        ```json
        {
            "detail": "Invalid role code"
        }
        ```
    """

    # Admin-only check
    role_obj = await get_user_role(db, current_user.role_id)
    if not role_obj or role_obj.role_code != "100":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can register new users.")

    # Check if username already exists
    result = await db.execute(select(user.User).filter(user.User.username == request.username))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Get role from role_code
    role_result = await db.execute(select(user.Role).filter(user.Role.role_code == request.role_code))
    role = role_result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=400, detail="Invalid role code")

    # Create user with default password
    new_user = user.User(
        username=request.username,
        hashed_password=auth.get_password_hash("test@123"),
        role_id=role.id
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return {"message": "User created successfully with default password: test@123"}

@router.post("/v1/login", tags=["Users"], response_model=LoginResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
        Authenticate a user and return a JWT access token.

        ### Request Headers:
        - `Content-Type`: application/json

        ### Path Parameters:
        - None

        ### Query Parameters:
        - None

        ### Request Body (application/json):
        - **username** (str): The user's username.
        - **password** (str): The user's password.

        #### Example:
        ```json
        {
            "username": "john_doe",
            "password": "strongPassword123"
        }
        ```

        ### Response (application/json):
        - **200 OK**: Successful authentication returns a JWT token.
        ```json
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer",
            "username":"john_doe",
            "user_id: 10,
            "role": "admin,
            "role_code":"100"
        }
        ```

        ### Error Responses:
        - **400 Bad Request**
            - Invalid credentials:
            ```json
            {
                "detail": "Invalid username or password"
            }
            ```

        ### Notes:
        - The returned JWT token should be included in the `Authorization` header for protected routes in this format:
        ```
        Authorization: Bearer <access_token>
        ```
        - The token includes the following claims in its payload:
            - **sub**: The username
            - **role**: The user's role (e.g., "admin", "teacher")
    """
    result = await db.execute(
        select(user.User)
        .filter(
            user.User.username == request.username,
            user.User.is_active == True
        )
        .options(joinedload(user.User.role))
    )
    user_record = result.scalar_one_or_none()

    if not user_record or not auth.verify_password(request.password, user_record.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    access_token = auth.create_access_token(
        data={"sub": user_record.username, "role": user_record.role.role_name}
    )

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user_record.id,
        username=user_record.username,
        role_name=user_record.role.role_name,
        role_code=user_record.role.role_code
    )

@router.get("/v1/roles", response_model=RoleListResponse, tags=["User Management"])
async def get_roles(db: AsyncSession = Depends(get_db)):
    """
    Retrieve all available user roles.

    ### Request Headers:
    - `Content-Type`: application/json
    - *(Optional)* `Authorization`: Bearer token (if roles are protected)

    ### Path Parameters:
    - None

    ### Query Parameters:
    - None

    ### Request Body:
    - None (GET request does not require a body)

    ### Response (application/json):
    - **200 OK**: List of available roles

    #### Response Schema:
    ```json
    {
    "data": [
        {
            "role_code": "100",
            "role_name": "admin"
        },
        {
            "role_code": "101",
            "role_name": "educator"
        }
            ]
    }
    ```

    ### Error Responses:
    - **500 Internal Server Error**: If there is a database or server issue

    ### Notes:
    - This endpoint can be used to populate dropdowns or options for user role selection during registration.
    - You can expand this in the future to include role descriptions or permissions if needed.
    """
    result = await db.execute(select(user.Role))
    roles = result.scalars().all()
    return RoleListResponse(data=roles)

@router.get("/v1/users", tags=["User Management"])
async def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Number of records per page"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Admin-only check
    role_obj = await get_user_role(db, current_user.role_id)
    if not role_obj or role_obj.role_code != "100":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins only")

    skip = (page - 1) * limit
    total_users = await count_active_users(db)
    users = await list_users_service(db, skip, limit)

    # Transform response to include role_name
    user_list = [
        {
            "id": u.id,
            "username": u.username,
            "role_id": u.role_id,
            "role_name": u.role.role_name if u.role else "Unknown",
            "is_active": u.is_active,
            "created_at": u.created_at,
            "updated_at": u.updated_at,
        }
        for u in users
    ]

    return {
        "page": page,
        "limit": limit,
        "total_users": total_users,
        "users": user_list
    }

@router.get("/v1/users/{user_id}", tags=["User Management"])
async def get_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Admin-only endpoint to fetch a single user's details by ID.
    """
    # Admin check
    role_obj = await get_user_role(db, current_user.role_id)
    if not role_obj or role_obj.role_code != "100":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins only")

    user_obj = await get_user_by_id_service(user_id, db)

    return {
        "id": user_obj.id,
        "username": user_obj.username,
        "role_id": user_obj.role_id,
        "role_name": user_obj.role.role_name if user_obj.role else "Unknown",
        "is_active": user_obj.is_active,
        "created_at": user_obj.created_at,
        "updated_at": user_obj.updated_at,
    }


@router.put("/v1/users/{user_id}/password", tags=["Users"])
async def update_user_password(
    user_id: int,
    payload: PasswordUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Update a user's password.
    - Users can update their own password.
    - Admins can update passwords for any user.
    """
    return await update_user_service(db, user_id, payload.new_password, current_user)

@router.put("/v1/users/{user_id}", tags=["User Management"])
async def update_user_info(
    user_id: int,
    payload: UserUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Admins can update a user's username, role, and active status.
    """
    return await update_user_info_service(
        db=db,
        user_id=user_id,
        username=payload.username,
        role_code=payload.role_code,
        is_active=payload.is_active,
        current_user=current_user
    )