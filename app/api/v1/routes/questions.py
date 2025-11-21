from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.question_service import get_chapter_topic_question_counts, get_questions_by_filters
from app.utils.auth import get_current_user
from app.schemas.questions import ChapterTopicQuestionCountResponse, ExamQuestionsResponse
from app.database import get_db

router = APIRouter()

@router.get("/v1/chapters_topics", tags=["Questions"], response_model=ChapterTopicQuestionCountResponse)
async def get_chapter_topic_question_counts_route(
    standard: str = Query(..., description="Class/standard (e.g., '10')"),
    medium_code: str = Query(..., description="Medium Code"),
    subject_code: str = Query(..., description="Subject Code"),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Retrieve chapters, topics, and their question counts for a given standard, medium, and subject.

    ### Request Headers:
    - `Content-Type`: application/json  
    - *(Optional)* `Authorization`: Bearer token (if access is restricted)

    ### Query Parameters:
    - **standard** (str, required): Standard/class (e.g., `"10"`).
    - **medium_code** (str, required): Medium code (e.g., `"2000"` for English).
    - **subject_code** (str, required): Subject code (e.g., `"3000"` for Social Science).

    ### Path Parameters:
    - None

    ### Request Body:
    - None (GET request does not require a body)

    ### Response (application/json):
    - **200 OK**: Returns a list of chapters, their topics, and associated question counts.

    #### Example Response:
    ```json
    {
      "data": [
        {
          "code": "1000",
          "name": "Climate and Natural Vegetation of India",
          "question_count": 50,
          "topics": [
            {
              "code": "10000",
              "name": "Distribution of rainfall",
              "question_count": 2,
              "subtopics": []
            },
            {
              "code": "10001",
              "name": "Introduction",
              "question_count": 28,
              "subtopics": []
            },
            {
              "code": "10002",
              "name": "Monsoon",
              "question_count": 7,
              "subtopics": []
            },
            {
              "code": "10004",
              "name": "The factors affecting the climate",
              "question_count": 10,
              "subtopics": []
            },
            {
              "code": "10005",
              "name": "Wildlife",
              "question_count": 3,
              "subtopics": []
            }
          ]
        },
        {
          "code": "1001",
          "name": "India's Foreign Policy",
          "question_count": 16,
          "topics": [
            {
              "code": "10006",
              "name": "Basic Determinants of a Foreign Policy",
              "question_count": 1,
              "subtopics": []
            },
            {
              "code": "10008",
              "name": "Main objectives of our Foreign Policy",
              "question_count": 2,
              "subtopics": []
            },
            {
              "code": "10009",
              "name": "Non-aligned movement",
              "question_count": 5,
              "subtopics": []
            }
          ]
        }
      ]
    }
    ```

    ### Error Responses:
    - **400 Bad Request**:
        ```json
        { "detail": "Missing required query parameters: standard, medium_code, or subject_code." }
        ```
    - **404 Not Found**:
        ```json
        { "detail": "No chapters or topics found for the given parameters." }
        ```
    - **500 Internal Server Error**:
        ```json
        { "detail": "Unexpected error occurred while retrieving chapter/topic data." }
        ```

    ### Notes:
    - Provides hierarchical data: **Chapters → Topics → Subtopics** with question counts.
    - Helps exam designers select chapters/topics with enough questions for exam design.
    - Can be used in question paper design workflows to show available content.
    """
    return await get_chapter_topic_question_counts(standard, medium_code, subject_code, db)

@router.get("/v1/questions", tags=["Questions"], response_model=ExamQuestionsResponse)
async def get_questions(
    type: str = Query(..., description="chapter or topic"),
    codes: str = Query(..., description="Comma-separated list of codes"),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
        Retrieve questions filtered by chapter or topic codes.

        ### Request Headers:
        - `Content-Type`: application/json  
        - *(Optional)* `Authorization`: Bearer token (if access is restricted)

        ### Query Parameters:
        - **type** (str, required): Must be either `"chapter"` or `"topic"`.
            - Indicates whether to fetch questions based on chapter or topic codes.
        - **codes** (str, required): Comma-separated list of codes.
            - Example: `"1000,1001"` for chapters or `"10100,10101"` for topics.

        ### Path Parameters:
        - None

        ### Request Body:
        - None (GET request does not require a body)

        ### Response (application/json):
        - **200 OK**: Returns question groups and detailed question data.

        #### Example Response:
        ```json
        {
        "qn_groups": [
            {
            "type": "chapter",
            "type_codes": ["1000"],
            "type_names": ["Climate and Natural Vegetation of India"],
            "no_of_qns": 50
            }
        ],
        "qns": [
            {
            "code": "Q1258163",
            "type": "MCQ",
            "marks": 1,
            "difficulty_level": "Medium",
            "grp_type": "chapter",
            "grp_type_name": "Climate and Natural Vegetation of India",
            "grp_type_code": "1000",
            "text": "Which is in the Eastern border of Tamil Nadu?"
            }
        ]
        }
        ```

        ### Error Responses:
        - **400 Bad Request**:
            ```json
            { "detail": "Invalid type. Must be 'chapter' or 'topic'." }
            ```
        - **404 Not Found**:
            ```json
            { "detail": "No questions found for the provided codes." }
            ```
        - **500 Internal Server Error**:
            ```json
            { "detail": "Unexpected error occurred while fetching questions." }
            ```

        ### Notes:
        - Use this endpoint to fetch questions tied to specific **chapters** or **topics**.
        - The response includes both:
            - **`qn_groups`**: Summary of selected chapter/topic groups with question counts.
            - **`qns`**: Detailed list of individual questions.
        - Useful for exam paper design and manual question selection workflows.
    """
    return await get_questions_by_filters(type, codes, db)