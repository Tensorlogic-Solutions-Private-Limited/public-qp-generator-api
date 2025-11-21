from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.metadata_service import (
    get_all_mediums, get_all_subjects, get_all_formats, get_all_question_types
)
from app.utils.auth import get_current_user
# from app.schemas.pydantic_models import MediumResponse, SubjectResponse, FormatResponse, QuestionTypeListResponse
# from app.schemas.pydantic_models import MediumBase, MediumResponse, SubjectBase, SubjectListResponse, FormatBase, FormatResponse, QuestionTypeBase, QuestionTypeListResponse
from app.schemas.metadata import MediumResponse, SubjectListResponse, FormatResponse, QuestionTypeListResponse

from app.database import get_db

router = APIRouter()

@router.get("/v1/mediums", tags=["Dropdowns"], response_model=MediumResponse)
async def get_mediums(db: AsyncSession = Depends(get_db),current_user=Depends(get_current_user)):
    """
        Retrieve all available mediums.

        ### Request Headers:
        - `Content-Type`: application/json
        - *(Optional)* `Authorization`: Bearer token (if access is restricted)

        ### Path Parameters:
        - None

        ### Query Parameters:
        - None

        ### Request Body:
        - None (GET request does not require a body)

        ### Response (application/json):
        - **200 OK**: Returns a list of mediums.

        #### Each item includes:
        - **medium_code** (str): Unique code representing the medium.
        - **medium_name** (str): Name of the medium (e.g., "English", "Hindi").

        ### Example Response:
        ```json
        [
            {
                "medium_code": "2000",
                "medium_name": "English"
            },
            {
                "medium_code": "2001",
                "medium_name": "Tamil"
            }
        ]
        ```

        ### Error Responses:
        - **500 Internal Server Error**: If a database or server error occurs.

        ### Notes:
        - Useful for categorizing or filtering educational content based on medium (e.g., language of instruction).
        - You can later enhance this model to include attributes like `active_status`, `display_order`, or descriptions.
    """
    return await get_all_mediums(db)

@router.get("/v1/subjects", tags=["Dropdowns"], response_model=SubjectListResponse)
async def get_subjects(db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    """
        Retrieve all available subjects.

        ### Request Headers:
        - `Content-Type`: application/json
        - *(Optional)* `Authorization`: Bearer token (if secured)

        ### Path Parameters:
        - None

        ### Query Parameters:
        - None

        ### Request Body:
        - None (This is a GET request)

        ### Response (application/json):
        - **200 OK**: A list of subjects.

        #### Each item includes:
        - **subject_code** (str): Code of the subject.
        - **subject_name** (str): Name of the subject.
        - **standard** (str): Class (standard) of the subject.
        - **medium_code** (str): Unique Code to the medium.

        ### Example Response:
        ```json
        {
            "data": [
                {
                    "subject_code": "1001",
                    "subject_name": "Science",
                    "standard": "10",
                    "medium_code": '2000'
                }
            ]
        }
        ```

        ### Error Responses:
        - **500 Internal Server Error**: If something goes wrong with the database.

        ### Notes:
        - Useful for dropdowns and filtering in design/question forms.
        - Can be extended with filtering by standard or medium_id.
    """
    return await get_all_subjects(db)

@router.get("/v1/formats", tags=["Dropdowns"], response_model=FormatResponse)
async def get_formats(db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    """
        Retrieve all available question formats.

        Returns a list of question formats used to categorize question structure or presentation.

        ### Headers:
        - `Content-Type`: `application/json`
        - *(Optional)* `Authorization`: `Bearer <token>` — Required if access is restricted.

        ### Response:
        - **200 OK**: List of question formats.

        #### Each item includes:
        - `qfm_format_code` (str): Unique format code (e.g., "5000").
        - `qfm_format_name` (str): Descriptive name (e.g., "Text").

        #### Example:
        ```json
        {
        "data": [
            {
            "format_code": "5000",
            "format_name": "Text"
            }
        ]
        }
        ```

        ### Errors:
        - **500 Internal Server Error**: Server/database error.

        ### Notes:
        Useful for filtering or categorizing questions. Can be extended with metadata like `active_status`, `description`, or `display_order`.
    """
    return await get_all_formats(db)

@router.get("/v1/question_types", tags=["Dropdowns"], response_model=QuestionTypeListResponse)
async def get_question_types(db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    """
        Retrieve all available question types.

        ### Request Headers:
        - `Content-Type`: application/json
        - *(Optional)* `Authorization`: Bearer token (if the endpoint is secured)

        ### Path Parameters:
        - None

        ### Query Parameters:
        - None

        ### Request Body:
        - None (This is a GET request)

        ### Response (application/json):
        - **200 OK**: A list of question types.

        #### Each item includes:
        - **id** (int): Unique identifier for the question type.
        - **qtm_type_code** (str): Unique code for the question type (e.g., "1000").
        - **qtm_type_name** (str): Descriptive name of the question type (e.g., "MCQ").

        ### Example Response:
        ```json
        {
        "data": [
                {
                    "id": 1,
                    "type_code": "1000",
                    "type_name": "MCQ"
                }
            ]
        }
        ```

        ### Error Responses:
        - **500 Internal Server Error**: If something goes wrong with the database connection or query.

        ### Notes:
        - This endpoint is helpful for populating question type dropdowns in forms or filtering question sets.
        - You can later extend the response model to include metadata like display order, status, or usage count.
    """
    
    return await get_all_question_types(db)