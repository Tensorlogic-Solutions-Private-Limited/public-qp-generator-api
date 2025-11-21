# from fastapi import APIRouter, Depends, HTTPException, Query, status
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select, func,join,not_, or_, and_
# from typing import List, Optional, Union
# from app.database import get_db
# from app.models import master
# from app.schemas.pydantic_models import *
# from sqlalchemy import select
# from sqlalchemy.orm import selectinload
# from sqlalchemy.exc import SQLAlchemyError
# import random
# import json
# from app.utils.pdf_util import wrap_text
# from datetime import datetime
# from sqlalchemy.orm import selectinload, joinedload
# from fastapi.responses import StreamingResponse
# from io import BytesIO
# from reportlab.pdfgen import canvas

# from fastapi import Depends
# from app.utils.auth import get_current_user
# from app.models import user
# from app.models.master import Taxonomy, Questions, Subject, Medium,Question_Type, Design, QuestionPaperDetails
# from app.models.user import Role
# import logging
# import random
# from collections import defaultdict
# from fastapi.responses import JSONResponse, StreamingResponse
# from io import BytesIO
# from reportlab.pdfgen import canvas

# logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO)

# router = APIRouter()


# def build_options(q, include_answers: bool = False):
#     options = [
#         {"id": "A", "text": q.qmt_option1},
#         {"id": "B", "text": q.qmt_option2},
#         {"id": "C", "text": q.qmt_option3},
#         {"id": "D", "text": q.qmt_option4},
#     ]
#     if include_answers:
#         for opt in options:
#             opt["is_correct"] = (
#                 (opt["id"] == "A" and q.qmt_correct_answer == "option A") or
#                 (opt["id"] == "B" and q.qmt_correct_answer == "option B") or
#                 (opt["id"] == "C" and q.qmt_correct_answer == "option C") or
#                 (opt["id"] == "D" and q.qmt_correct_answer == "option D")
#             )
#     return options


# @router.get("/v1/question_types", response_model=QuestionTypeListResponse, tags=["Design Dropdowns"])
# async def get_question_types(
#     db: AsyncSession = Depends(get_db),
#     current_user: user.User = Depends(get_current_user)
# ):
    # """
    # Retrieve all available question types.

    # ### Request Headers:
    # - `Content-Type`: application/json
    # - *(Optional)* `Authorization`: Bearer token (if the endpoint is secured)

    # ### Path Parameters:
    # - None

    # ### Query Parameters:
    # - None

    # ### Request Body:
    # - None (This is a GET request)

    # ### Response (application/json):
    # - **200 OK**: A list of question types.

    # #### Each item includes:
    # - **id** (int): Unique identifier for the question type.
    # - **qtm_type_code** (str): Unique code for the question type (e.g., "1000").
    # - **qtm_type_name** (str): Descriptive name of the question type (e.g., "MCQ").

    # ### Example Response:
    # ```json
    # {
    # "data": [
    #         {
    #             "id": 1,
    #             "type_code": "1000",
    #             "type_name": "MCQ"
    #         }
    #     ]
    # }
    # ```

    # ### Error Responses:
    # - **500 Internal Server Error**: If something goes wrong with the database connection or query.

    # ### Notes:
    # - This endpoint is helpful for populating question type dropdowns in forms or filtering question sets.
    # - You can later extend the response model to include metadata like display order, status, or usage count.
    # """
#     result = await db.execute(select(master.Question_Type))
#     question_types = result.scalars().all()

#     question_types_data = [
#         QuestionTypeBase(
#             id=question_type.id,
#             type_code=question_type.qtm_type_code,
#             type_name=question_type.qtm_type_name
#         )
#         for question_type in question_types
#     ]

#     return QuestionTypeListResponse(data=question_types_data)

# @router.get(
#     "/v1/subjects",
#     response_model=SubjectListResponse,
#     tags=["Design Dropdowns"]
# )
# async def get_subjects(
#     db: AsyncSession = Depends(get_db),
#     current_user: user.User = Depends(get_current_user),
# ):
    # """
    # Retrieve all available subjects.

    # ### Request Headers:
    # - `Content-Type`: application/json
    # - *(Optional)* `Authorization`: Bearer token (if secured)

    # ### Path Parameters:
    # - None

    # ### Query Parameters:
    # - None

    # ### Request Body:
    # - None (This is a GET request)

    # ### Response (application/json):
    # - **200 OK**: A list of subjects.

    # #### Each item includes:
    # - **subject_code** (str): Code of the subject.
    # - **subject_name** (str): Name of the subject.
    # - **standard** (str): Class (standard) of the subject.
    # - **medium_code** (str): Unique Code to the medium.

    # ### Example Response:
    # ```json
    # {
    #     "data": [
    #         {
    #             "subject_code": "1001",
    #             "subject_name": "Science",
    #             "standard": "10",
    #             "medium_code": '2000'
    #         }
    #     ]
    # }
    # ```

    # ### Error Responses:
    # - **500 Internal Server Error**: If something goes wrong with the database.

    # ### Notes:
    # - Useful for dropdowns and filtering in design/question forms.
    # - Can be extended with filtering by standard or medium_id.
    # """
#     result = await db.execute(
#         select(master.Subject).options(selectinload(master.Subject.medium))
#     )
#     subjects = result.scalars().all()

#     # Inline mapper: map ORM to Pydantic
#     response_data = [
#         SubjectBase(
#             subject_code=subject.smt_subject_code,
#             subject_name=subject.smt_subject_name,
#             standard=subject.smt_standard,
#             medium_code=subject.medium.mmt_medium_code
#         )
#         for subject in subjects
#     ]

#     return SubjectListResponse(data=response_data)

# @router.get("/v1/mediums", response_model=MediumResponse, tags=["Design Dropdowns"])
# async def get_mediums(
#     db: AsyncSession = Depends(get_db),
#     current_user: user.User = Depends(get_current_user)
# ):
    # """
    # Retrieve all available mediums.

    # ### Request Headers:
    # - `Content-Type`: application/json
    # - *(Optional)* `Authorization`: Bearer token (if access is restricted)

    # ### Path Parameters:
    # - None

    # ### Query Parameters:
    # - None

    # ### Request Body:
    # - None (GET request does not require a body)

    # ### Response (application/json):
    # - **200 OK**: Returns a list of mediums.

    # #### Each item includes:
    # - **medium_code** (str): Unique code representing the medium.
    # - **medium_name** (str): Name of the medium (e.g., "English", "Hindi").

    # ### Example Response:
    # ```json
    # [
    #     {
    #         "medium_code": "2000",
    #         "medium_name": "English"
    #     },
    #     {
    #         "medium_code": "2001",
    #         "medium_name": "Tamil"
    #     }
    # ]
    # ```

    # ### Error Responses:
    # - **500 Internal Server Error**: If a database or server error occurs.

    # ### Notes:
    # - Useful for categorizing or filtering educational content based on medium (e.g., language of instruction).
    # - You can later enhance this model to include attributes like `active_status`, `display_order`, or descriptions.
    # """
#     result = await db.execute(select(master.Medium))
#     mediums = result.scalars().all()

#     # Map ORM to Pydantic
#     medium_data = [
#         MediumBase(
#             medium_code=medium.mmt_medium_code,
#             medium_name=medium.mmt_medium_name
#         )
#         for medium in mediums
#     ]

#     return MediumResponse(data=medium_data)

# @router.get("/v1/question_formats", response_model=FormatResponse, tags=["Design Dropdowns"])
# async def get_formats(
#     db: AsyncSession = Depends(get_db),
#     # current_user: user.User = Depends(get_current_user)
# ):
    # """
    # Retrieve all available question formats.

    # Returns a list of question formats used to categorize question structure or presentation.

    # ### Headers:
    # - `Content-Type`: `application/json`
    # - *(Optional)* `Authorization`: `Bearer <token>` — Required if access is restricted.

    # ### Response:
    # - **200 OK**: List of question formats.

    # #### Each item includes:
    # - `qfm_format_code` (str): Unique format code (e.g., "5000").
    # - `qfm_format_name` (str): Descriptive name (e.g., "Text").

    # #### Example:
    # ```json
    # {
    #   "data": [
    #     {
    #       "format_code": "5000",
    #       "format_name": "Text"
    #     }
    #   ]
    # }
    # ```

    # ### Errors:
    # - **500 Internal Server Error**: Server/database error.

    # ### Notes:
    # Useful for filtering or categorizing questions. Can be extended with metadata like `active_status`, `description`, or `display_order`.
    # """
#     result = await db.execute(select(master.Question_Format))
#     formats = result.scalars().all()
#     return FormatResponse(data=formats)


# @router.get(
#     "/v1/chapters_topics",
#     tags=["Groups"],
# )
# async def get_chapter_topic_question_counts(
#     standard: str = Query(..., description="Class/standard (e.g., '10')"),
#     medium_code: str = Query(..., description="Medium Code"),
#     subject_code: str = Query(..., description="Subject Code"),
#     db: AsyncSession = Depends(get_db),
#     current_user: user.User = Depends(get_current_user),
# ):
#     """
#             Retrieve chapter → topic → subtopic question counts filtered by standard, medium, and subject.

#     ### Request Headers:
#     - `Content-Type`: application/json
#     - *(Optional)* `Authorization`: Bearer token (if secured)

#     ### Path Parameters:
#     - None

#     ### Query Parameters:
#     - **standard** (str, required): Class/standard (e.g., "10").
#     - **medium_code** (str, required): Medium code (e.g., "2000").
#     - **subject_code** (str, required): Subject code (e.g., "3000").

#     ### Request Body:
#     - None (This is a GET request)

#     ### Response (application/json):
#     - **200 OK**: A list of chapters with their topics and question counts.

#     #### Each chapter includes:
#     - **code** (str): Chapter code.
#     - **name** (str): Chapter name.
#     - **question_count** (int): Total questions under this chapter.
#     - **topics** (list):
#       - **code** (str): Topic code.
#       - **name** (str): Topic name.
#       - **question_count** (int): Total questions under this topic.
#       - **subtopics** (list): Empty list (reserved for future use).

#     ### Example Response:
#     ```json
#     {
#       "chapters": [
#         {
#           "code": "CH01",
#           "name": "Introduction",
#           "question_count": 20,
#           "topics": [
#             {
#               "code": "TP01",
#               "name": "Basics",
#               "question_count": 10,
#               "subtopics": []
#             }
#           ]
#         }
#       ]
#     }
#     ```

#     ### Error Responses:
#     - **500 Internal Server Error**: If something goes wrong with the database.

#     ### Notes:
#     - Designed for hierarchical display in UIs (e.g., select chapter → view topics).
#     """

#     # Chapter-level
#     chapter_stmt = (
#         select(
#             Taxonomy.stm_chapter_code.label("chapter_code"),
#             Taxonomy.stm_chapter_name.label("chapter_name"),
#             func.count(Questions.id).label("chapter_question_count")
#         )
#         .join(Questions, Questions.qmt_taxonomy_id == Taxonomy.id)
#         .join(Subject, Taxonomy.stm_subject_id == Subject.id)
#         .join(Medium, Taxonomy.stm_medium_id == Medium.id)
#         .where(
#             Taxonomy.stm_standard == standard,
#             Subject.smt_subject_code == subject_code,
#             Medium.mmt_medium_code == medium_code,
#         )
#         .group_by(Taxonomy.stm_chapter_code, Taxonomy.stm_chapter_name)
#         .order_by(Taxonomy.stm_chapter_code)
#     )
#     chapter_result = await db.execute(chapter_stmt)
#     chapter_rows = chapter_result.all()

#     # Topic-level
#     topic_stmt = (
#         select(
#             Taxonomy.stm_chapter_code.label("chapter_code"),
#             Taxonomy.stm_topic_code.label("topic_code"),
#             Taxonomy.stm_topic_name.label("topic_name"),
#             func.count(Questions.id).label("topic_question_count")
#         )
#         .join(Questions, Questions.qmt_taxonomy_id == Taxonomy.id)
#         .join(Subject, Taxonomy.stm_subject_id == Subject.id)
#         .join(Medium, Taxonomy.stm_medium_id == Medium.id)
#         .where(
#             Taxonomy.stm_standard == standard,
#             Subject.smt_subject_code == subject_code,
#             Medium.mmt_medium_code == medium_code,
#         )
#         .group_by(
#             Taxonomy.stm_chapter_code,
#             Taxonomy.stm_topic_code,
#             Taxonomy.stm_topic_name
#         )
#         .order_by(
#             Taxonomy.stm_chapter_code,
#             Taxonomy.stm_topic_code
#         )
#     )
#     topic_result = await db.execute(topic_stmt)
#     topic_rows = topic_result.all()

#     # Group topics under each chapter
#     chapter_to_topics = defaultdict(list)
#     for topic in topic_rows:
#         chapter_to_topics[topic.chapter_code].append({
#             "code": topic.topic_code,
#             "name": topic.topic_name,
#             "question_count": topic.topic_question_count,
#             "subtopics": []  # empty list since no data 
#         })

#     # Final nested structure
#     final_chapters = []
#     for chapter in chapter_rows:
#         final_chapters.append({
#             "code": chapter.chapter_code,
#             "name": chapter.chapter_name,
#             "question_count": chapter.chapter_question_count,
#             "topics": chapter_to_topics.get(chapter.chapter_code, [])
#         })

#     return {"chapters": final_chapters}

# @router.get(
#     "/v1/questions",
#     response_model=ExamQuestionsResponse,
#     tags=["Groups"]
# )
# async def get_questions(
#     type: str = Query(..., description="chapter or topic"),
#     codes: str = Query(..., description="Comma-separated list of codes"),
#     db: AsyncSession = Depends(get_db),
#     current_user: user.User = Depends(get_current_user)
# ):
#     """
#     Retrieve questions filtered by chapter or topic codes.

#     ### Request Headers:
#     - `Content-Type`: application/json
#     - *(Optional)* `Authorization`: Bearer token (if secured)

#     ### Path Parameters:
#     - None

#     ### Query Parameters:
#     - **type** (str, required): Must be either `"chapter"` or `"topic"`.
#     - **codes** (str, required): Comma-separated list of chapter/topic codes.

#     ### Request Body:
#     - None (This is a GET request)

#     ### Response (application/json):
#     - **200 OK**: Groups of questions and their details.

#     #### Top-level fields:
#     - **qn_groups** (list):
#       - **type** (str): "chapter" or "topic".
#       - **type_codes** (list of str): Codes of groups.
#       - **type_names** (list of str): Names of groups.
#       - **no_of_qns** (int): Total number of questions.

#     - **qns** (list):
#       - **code** (str): Question code.
#       - **type** (str): Question type (e.g., "MCQ").
#       - **marks** (int): Marks for the question.
#       - **difficulty_level** (str): Difficulty level.
#       - **grp_type** (str): "chapter" or "topic".
#       - **grp_type_name** (str): Name of the chapter/topic.
#       - **grp_type_code** (str): Code of the chapter/topic.
#       - **text** (str): Question text.

#     ### Example Response:
#     ```json
#     {
#       "qn_groups": [
#         {
#           "type": "chapter",
#           "type_codes": ["CH01"],
#           "type_names": ["Introduction"],
#           "no_of_qns": 2
#         }
#       ],
#       "qns": [
#         {
#           "code": "Q001",
#           "type": "MCQ",
#           "marks": 2,
#           "difficulty_level": "Medium",
#           "grp_type": "chapter",
#           "grp_type_name": "Introduction",
#           "grp_type_code": "CH01",
#           "text": "What is photosynthesis?"
#         }
#       ]
#     }
#     ```

#     ### Error Responses:
#     - **400 Bad Request**: If `type` is not "chapter" or "topic".
#     - **500 Internal Server Error**: For unexpected server errors.

#     ### Notes:
#     - Use this endpoint to fetch question details for selected chapters or topics.
#     - Supports multiple codes in a single request (comma-separated).
#     """
#     if type not in ["chapter", "topic"]:
#         raise HTTPException(status_code=400, detail="Invalid type. Must be 'chapter' or 'topic'.")

#     # Split codes
#     code_list = [c.strip() for c in codes.split(",") if c.strip()]
#     if not code_list:
#         return ExamQuestionsResponse(qn_groups=[], qns=[])

#     # Determine filter column
#     filter_column = Taxonomy.stm_chapter_code if type == "chapter" else Taxonomy.stm_topic_code

#     # Query
#     stmt = (
#         select(Questions)
#         .join(Taxonomy, Questions.qmt_taxonomy_id == Taxonomy.id)
#         .join(Question_Type, Questions.qmt_type_id == Question_Type.id)
#         .where(filter_column.in_(code_list))
#         .options(joinedload(Questions.taxonomy), joinedload(Questions.type))
#     )
#     result = await db.execute(stmt)
#     questions = result.scalars().all()

#     # Build response lists
#     qns_list: List[ExamQuestionResponse] = []
#     type_codes_set = set()
#     type_names_set = set()

#     for q in questions:
#         taxonomy = q.taxonomy
#         grp_code = taxonomy.stm_chapter_code if type == "chapter" else taxonomy.stm_topic_code
#         grp_name = taxonomy.stm_chapter_name if type == "chapter" else taxonomy.stm_topic_name
#         type_codes_set.add(grp_code)
#         type_names_set.add(grp_name)

#         qns_list.append(ExamQuestionResponse(
#             code=q.qmt_question_code,
#             type=q.type.qtm_type_name,
#             marks=q.qmt_marks,
#             difficulty_level="Medium",
#             grp_type=type,
#             grp_type_name=grp_name,
#             grp_type_code=grp_code,
#             text=q.qmt_question_text
#         ))

#     qn_groups = [ExamQuestionGroupResponse(
#         type=type,
#         type_codes=list(type_codes_set),
#         type_names=list(type_names_set),
#         no_of_qns=len(qns_list)
#     )]

#     return ExamQuestionsResponse(
#         qn_groups=qn_groups,
#         qns=qns_list
#     )

# # @router.post(
# #     "/v1/question_papers",
# #     tags=["Create Exams and Generate QPs"]
# # )
# # async def create_exams_question_papers(
# #     payload: DesignCreate,
# #     db: AsyncSession = Depends(get_db),
# #     current_user: user.User = Depends(get_current_user)
# # ):
# #     """
# #     Creates a new Design by resolving all foreign key codes to IDs,
# #     ensures enough questions exist, then creates Design and Question Papers.
# #     """

# #     # ----------------------------------------------------------
# #     # Get User's Role (to determine if they are admin)
# #     # ----------------------------------------------------------
# #     role_stmt = select(Role).where(Role.id == current_user.role_id)
# #     role_result = await db.execute(role_stmt)
# #     role_obj = role_result.scalar_one_or_none()

# #     if not role_obj:
# #         raise HTTPException(status_code=404, detail="User role not found.")

# #     include_correct_answers = role_obj.role_code == '100'

# #     # ----------------------------------------------------------
# #     # Check if design with this name already exists
# #     # ----------------------------------------------------------
# #     existing_design = await db.execute(
# #         select(Design).where(Design.dm_design_name == payload.exam_name)
# #     )
# #     if existing_design.scalar_one_or_none():
# #         raise HTTPException(status_code=409, detail="Design with this name already exists.")

# #     # ----------------------------------------------------------
# #     # Resolve Foreign Keys (Exam Type, Subject, Medium)
# #     # ----------------------------------------------------------
# #     exam_type_obj = await db.scalar(
# #         select(Question_Type).where(Question_Type.qtm_type_code == payload.exam_type_code)
# #     )
# #     if not exam_type_obj:
# #         raise HTTPException(status_code=404, detail=f"Exam Type code '{payload.exam_type_code}' not found.")

# #     subject_obj = await db.scalar(
# #         select(Subject).where(Subject.smt_subject_code == payload.subject_code)
# #     )
# #     if not subject_obj:
# #         raise HTTPException(status_code=404, detail=f"Subject code '{payload.subject_code}' not found.")

# #     medium_obj = await db.scalar(
# #         select(Medium).where(Medium.mmt_medium_code == payload.medium_code)
# #     )
# #     if not medium_obj:
# #         raise HTTPException(status_code=404, detail=f"Medium code '{payload.medium_code}' not found.")

# #     # ----------------------------------------------------------
# #     # Build Question Selection
# #     # ----------------------------------------------------------
# #     if payload.qns.type == 'chapter':
# #         condition = Taxonomy.stm_chapter_code.in_(payload.qns.codes)
# #     elif payload.qns.type == 'topic':
# #         condition = Taxonomy.stm_topic_code.in_(payload.qns.codes)
# #     else:
# #         raise HTTPException(status_code=400, detail="Invalid selection type.")

# #     questions_result = await db.execute(
# #         select(Questions)
# #         .join(Taxonomy)
# #         .where(condition)
# #         .order_by(Taxonomy.stm_chapter_code, Taxonomy.stm_topic_code)
# #     )
# #     questions = questions_result.scalars().all()

# #     total_qtn_code = [q.qmt_question_code for q in questions]
# #     excluded_codes = set(payload.qns.qtn_codes_to_exclude or [])
# #     selected_question_codes = [code for code in total_qtn_code if code not in excluded_codes]

# #     # ----------------------------------------------------------
# #     # Validate Enough Questions
# #     # ----------------------------------------------------------
# #     required_qtns = payload.no_of_sets * payload.total_questions
# #     if len(selected_question_codes) < required_qtns:
# #         raise HTTPException(
# #             status_code=400,
# #             detail=f"Not enough questions available: required {required_qtns}, got {len(selected_question_codes)}"
# #         )

# #     # ----------------------------------------------------------
# #     # Split into Sets
# #     # ----------------------------------------------------------
# #     set_chunks = [
# #         selected_question_codes[i * payload.total_questions : (i + 1) * payload.total_questions]
# #         for i in range(payload.no_of_sets)
# #     ]

# #     # ----------------------------------------------------------
# #     # Generate Unique Design Code (EXM00001 style)
# #     # ----------------------------------------------------------
# #     MAX_ATTEMPTS = 5
# #     attempts = 0
# #     new_design_code = None

# #     while attempts < MAX_ATTEMPTS:
# #         result = await db.execute(
# #             select(Design.dm_design_code).where(Design.dm_design_code.like("EXM%"))
# #         )
# #         all_codes = result.scalars().all()

# #         max_number = 0
# #         for code in all_codes:
# #             try:
# #                 number_part = code.replace("EXM", "")
# #                 number = int(number_part)
# #                 if number > max_number:
# #                     max_number = number
# #             except (ValueError, AttributeError):
# #                 continue

# #         next_number = max_number + 1
# #         candidate_code = f"EXM{next_number:05d}"

# #         exists = await db.scalar(
# #             select(Design.id).where(Design.dm_design_code == candidate_code)
# #         )
# #         if not exists:
# #             new_design_code = candidate_code
# #             break

# #         attempts += 1

# #     if not new_design_code:
# #         raise HTTPException(status_code=409, detail="Unable to generate unique design code after multiple attempts.")

# #     # ----------------------------------------------------------
# #     # Create Design
# #     # ----------------------------------------------------------
# #     new_design = Design(
# #         dm_design_name=payload.exam_name,
# #         dm_design_code=new_design_code,
# #         dm_exam_type_id=exam_type_obj.id,
# #         dm_exam_mode=payload.exam_mode,
# #         dm_total_time=payload.total_time,
# #         dm_total_questions=payload.total_questions,
# #         dm_no_of_versions=payload.no_of_versions,
# #         dm_no_of_sets=payload.no_of_sets,
# #         dm_subject_id=subject_obj.id,
# #         dm_medium_id=medium_obj.id,
# #         dm_standard=payload.standard,
# #         dm_status='closed',
# #         dm_total_question_codes=total_qtn_code,
# #         created_by=current_user.id
# #     )
# #     db.add(new_design)
# #     await db.commit()
# #     await db.refresh(new_design)

# #     # ----------------------------------------------------------
# #     # Create Question Paper Details
# #     # ----------------------------------------------------------
# #     for set_index, question_set in enumerate(set_chunks, start=1):
# #         for version in range(1, payload.no_of_versions + 1):
# #             shuffled_questions = question_set.copy()
# #             random.shuffle(shuffled_questions)

# #             paper_id = f"QP{new_design.id:02d}S{set_index:02d}V{version:02d}"
# #             paper_detail = QuestionPaperDetails(
# #                 qpd_paper_id=paper_id,
# #                 qpd_q_codes=shuffled_questions,
# #                 qpd_total_time=payload.total_time,
# #                 qpd_total_questions=payload.total_questions,
# #                 qpd_design_name=payload.exam_name,
# #                 qpd_design_id=new_design.id,
# #                 created_by=current_user.id
# #             )
# #             db.add(paper_detail)

# #     await db.commit()

# #     # ----------------------------------------------------------
# #     # Fetch Created Papers
# #     # ----------------------------------------------------------
# #     papers_result = await db.execute(
# #         select(QuestionPaperDetails).where(QuestionPaperDetails.qpd_design_id == new_design.id)
# #     )
# #     papers = papers_result.scalars().all()

# #     # ----------------------------------------------------------
# #     # Collect Question Codes
# #     # ----------------------------------------------------------
# #     all_codes = set(code for paper in papers for code in paper.qpd_q_codes)

# #     questions_result = await db.execute(
# #         select(Questions).where(Questions.qmt_question_code.in_(all_codes))
# #     )
# #     questions_list = questions_result.scalars().all()
# #     questions_map = {q.qmt_question_code: q for q in questions_list}

# #     # ----------------------------------------------------------
# #     # Build Question Papers Response
# #     # ----------------------------------------------------------
# #     question_papers_response = []

# #     for paper in papers:
# #         qns_list = []
# #         for code in paper.qpd_q_codes:
# #             q = questions_map.get(code)
# #             if not q:
# #                 continue

# #             options_list = build_options(q, include_answers=include_correct_answers)

# #             qns_list.append({
# #                 "id": q.qmt_question_code,
# #                 "text": q.qmt_question_text,
# #                 "options": options_list
# #             })

# #         question_papers_response.append({
# #             "id": paper.qpd_paper_id,
# #             "qns": qns_list
# #         })

# #     # ----------------------------------------------------------
# #     # Return Final Response
# #     # ----------------------------------------------------------
# #     return {
# #         "exam_name": new_design.dm_design_name,
# #         "exam_code": new_design.dm_design_code,
# #         "number_of_sets": new_design.dm_no_of_sets,
# #         "number_of_versions": new_design.dm_no_of_versions,
# #         "no_of_qns": new_design.dm_total_questions,
# #         "subject": subject_obj.smt_subject_name,
# #         "medium": medium_obj.mmt_medium_name,
# #         "exam_type": exam_type_obj.qtm_type_name,
# #         "question_papers": question_papers_response
# #     }

# @router.post(
#     "/v1/question_papers",
#     tags=["Create Exams and Generate QPs"]
# )
# async def create_exams_question_papers(
#     payload: DesignCreate,
#     db: AsyncSession = Depends(get_db),
#     current_user: user.User = Depends(get_current_user)
# ):
#     """
#     Create a new Exam Design and generate question papers with multiple sets and versions.

#     ### Request Headers:
#     - `Content-Type`: application/json
#     - *(Optional)* `Authorization`: Bearer token (if secured)

#     ### Path Parameters:
#     - None

#     ### Query Parameters:
#     - None

#     ---

#     ### Request Body (application/json):
#     - **exam_name** (str, required): Unique name of the exam.
#     - **exam_type_code** (str, required): Code for the exam type (e.g., "1000").
#     - **subject_code** (str, required): Code for the subject.
#     - **medium_code** (str, required): Code for the medium.
#     - **exam_mode** (str, required): Mode of the exam (e.g., "online", "offline").
#     - **total_time** (int, required): Duration of the exam in minutes.
#     - **total_questions** (int, required): Number of questions per paper.
#     - **no_of_versions** (int, required): Number of versions per set.
#     - **no_of_sets** (int, required): Number of unique sets to generate.
#     - **standard** (str, optional): Standard/class (e.g., "10").
#     - **qns** (list of objects, required): Multiple selection groups.

#     #### Each `qns` item:
#     - **type** (str): `"chapter"` or `"topic"`.
#     - **codes** (list of str): Codes to include (chapter/topic codes).
#     - **qtn_codes_to_exclude** (list of str, optional): Question codes to exclude.

#     ---

#     ### Example Request Body:
#     ```json
#     {
#       "exam_name": "My Exam",
#       "exam_type_code": "1000",
#       "subject_code": "3000",
#       "medium_code": "2000",
#       "exam_mode": "online",
#       "total_time": 90,
#       "total_questions": 50,
#       "no_of_versions": 2,
#       "no_of_sets": 3,
#       "standard": "10",
#       "qns": [
#         {
#           "type": "chapter",
#           "codes": ["CHAP01", "CHAP02"],
#           "qtn_codes_to_exclude": ["Q12345", "Q67890"]
#         },
#         {
#           "type": "topic",
#           "codes": ["TP01", "TP02"],
#           "qtn_codes_to_exclude": ["Q12345", "Q67890"]
#         }
#       ]
#     }
#     ```

#     ---

#     ### Response (application/json):
#     **200 OK**: Returns the created exam design and all generated question papers.

#     #### Top-level fields:
#     - **exam_name** (str): Name of the exam.
#     - **exam_code** (str): Auto-generated unique exam code (e.g., "EXM00001").
#     - **number_of_sets** (int): Number of sets generated.
#     - **number_of_versions** (int): Number of versions per set.
#     - **no_of_qns** (int): Number of questions per paper.
#     - **subject** (str): Subject name.
#     - **medium** (str): Medium name.
#     - **exam_type** (str): Exam type name.
#     - **question_papers** (list):
#       - **id** (str): Unique paper ID (e.g., "QP01S01V01").
#       - **qns** (list):
#         - **id** (str): Question code.
#         - **text** (str): Question text.
#         - **options** (list): Options for the question (with/without correct answer depending on user role).

#     ---

#     ### Example Response:
#     ```json
#     {
#   "exam_name": "Final Science Exam 1",
#   "exam_code": "EXM00010",
#   "number_of_sets": 2,
#   "number_of_versions": 3,
#   "no_of_qns": 5,
#   "subject": "Social Science",
#   "medium": "English",
#   "exam_type": "MCQ",
#   "question_papers": [
#     {
#       "id": "QP41S01V01",
#       "qns": [
#         {
#           "id": "Q1327552",
#           "text": "What is British climate?",
#           "options": [
#             {
#               "id": "A",
#               "text": "Extremely hot and humid",
#               "is_correct": false
#             },
#             {
#               "id": "B",
#               "text": "Mild and wet",
#               "is_correct": true
#             },
#             {
#               "id": "C",
#               "text": "Extremely cold and dry",
#               "is_correct": false
#             },
#             {
#               "id": "D",
#               "text": "Hot and dry",
#               "is_correct": false
#             }......
#     ```

#     ---

#     ### Error Responses:
#     - **400 Bad Request**:
#       - Invalid selection type in `qns` (must be "chapter" or "topic").
#       - Not enough questions available to generate the required sets/versions.

#     - **404 Not Found**:
#       - User role not found.
#       - Exam type, subject, or medium code not found.

#     - **409 Conflict**:
#       - Exam design with the same name already exists.
#       - Unable to generate unique design code.

#     - **500 Internal Server Error**:
#       - For unexpected server errors.

#     ---

#     ### Notes:
#     - This endpoint is used to create new exam designs with multiple question selection groups (chapters/topics).
#     - It ensures sufficient questions exist to fulfill all sets and versions.
#     - Excluded question codes are removed before allocation.
#     - Only users with an admin role can view correct answer flags in the response.
#     """


#     # ----------------------------------------------------------
#     # Get User's Role
#     # ----------------------------------------------------------
#     role_stmt = select(Role).where(Role.id == current_user.role_id)
#     role_result = await db.execute(role_stmt)
#     role_obj = role_result.scalar_one_or_none()
#     if not role_obj:
#         raise HTTPException(status_code=404, detail="User role not found.")
#     include_correct_answers = role_obj.role_code == '100'

#     # ----------------------------------------------------------
#     # Check if design name already exists
#     # ----------------------------------------------------------
#     existing_design = await db.scalar(
#         select(Design).where(Design.dm_design_name == payload.exam_name)
#     )
#     if existing_design:
#         raise HTTPException(status_code=409, detail="Design with this name already exists.")

#     # ----------------------------------------------------------
#     # Resolve Foreign Keys
#     # ----------------------------------------------------------
#     exam_type_obj = await db.scalar(
#         select(Question_Type).where(Question_Type.qtm_type_code == payload.exam_type_code)
#     )
#     if not exam_type_obj:
#         raise HTTPException(status_code=404, detail=f"Exam Type code '{payload.exam_type_code}' not found.")

#     subject_obj = await db.scalar(
#         select(Subject).where(Subject.smt_subject_code == payload.subject_code)
#     )
#     if not subject_obj:
#         raise HTTPException(status_code=404, detail=f"Subject code '{payload.subject_code}' not found.")

#     medium_obj = await db.scalar(
#         select(Medium).where(Medium.mmt_medium_code == payload.medium_code)
#     )
#     if not medium_obj:
#         raise HTTPException(status_code=404, detail=f"Medium code '{payload.medium_code}' not found.")

#     # ----------------------------------------------------------
#     # Build Question Selection from Multiple qns groups
#     # ----------------------------------------------------------
#     all_question_codes = set()
#     all_excluded_codes = set()

#     for qn_group in payload.qns:
#         if qn_group.type == 'chapter':
#             condition = Taxonomy.stm_chapter_code.in_(qn_group.codes)
#         elif qn_group.type == 'topic':
#             condition = Taxonomy.stm_topic_code.in_(qn_group.codes)
#         else:
#             raise HTTPException(status_code=400, detail=f"Invalid selection type: {qn_group.type}")

#         questions_result = await db.execute(
#             select(Questions)
#             .join(Taxonomy)
#             .where(condition)
#             .order_by(Taxonomy.stm_chapter_code, Taxonomy.stm_topic_code)
#         )
#         questions = questions_result.scalars().all()

#         all_question_codes.update(q.qmt_question_code for q in questions)
#         all_excluded_codes.update(qn_group.qtn_codes_to_exclude or [])

#     selected_question_codes = [code for code in all_question_codes if code not in all_excluded_codes]

#     # ----------------------------------------------------------
#     # Validate Enough Questions
#     # ----------------------------------------------------------
#     required_qtns = payload.no_of_sets * payload.total_questions
#     if len(selected_question_codes) < required_qtns:
#         raise HTTPException(
#             status_code=400,
#             detail=f"Not enough questions available: required {required_qtns}, got {len(selected_question_codes)}"
#         )

#     # ----------------------------------------------------------
#     # Split into Sets
#     # ----------------------------------------------------------
#     set_chunks = [
#         selected_question_codes[i * payload.total_questions : (i + 1) * payload.total_questions]
#         for i in range(payload.no_of_sets)
#     ]

#     # ----------------------------------------------------------
#     # Generate Unique Design Code
#     # ----------------------------------------------------------
#     MAX_ATTEMPTS = 5
#     attempts = 0
#     new_design_code = None

#     while attempts < MAX_ATTEMPTS:
#         result = await db.execute(
#             select(Design.dm_design_code).where(Design.dm_design_code.like("EXM%"))
#         )
#         all_codes = result.scalars().all()

#         max_number = 0
#         for code in all_codes:
#             try:
#                 number_part = code.replace("EXM", "")
#                 number = int(number_part)
#                 if number > max_number:
#                     max_number = number
#             except (ValueError, AttributeError):
#                 continue

#         next_number = max_number + 1
#         candidate_code = f"EXM{next_number:05d}"

#         exists = await db.scalar(
#             select(Design.id).where(Design.dm_design_code == candidate_code)
#         )
#         if not exists:
#             new_design_code = candidate_code
#             break

#         attempts += 1

#     if not new_design_code:
#         raise HTTPException(status_code=409, detail="Unable to generate unique design code after multiple attempts.")

#     # ----------------------------------------------------------
#     # Create Design
#     # ----------------------------------------------------------
#     new_design = Design(
#         dm_design_name=payload.exam_name,
#         dm_design_code=new_design_code,
#         dm_exam_type_id=exam_type_obj.id,
#         dm_exam_mode=payload.exam_mode,
#         dm_total_time=payload.total_time,
#         dm_total_questions=payload.total_questions,
#         dm_no_of_versions=payload.no_of_versions,
#         dm_no_of_sets=payload.no_of_sets,
#         dm_subject_id=subject_obj.id,
#         dm_medium_id=medium_obj.id,
#         dm_standard=payload.standard,
#         dm_status='closed',
#         dm_total_question_codes=list(all_question_codes),
#         created_by=current_user.id
#     )
#     db.add(new_design)
#     await db.commit()
#     await db.refresh(new_design)

#     # ----------------------------------------------------------
#     # Create Question Paper Details
#     # ----------------------------------------------------------
#     for set_index, question_set in enumerate(set_chunks, start=1):
#         for version in range(1, payload.no_of_versions + 1):
#             shuffled_questions = question_set.copy()
#             random.shuffle(shuffled_questions)

#             paper_id = f"QP{new_design.id:02d}S{set_index:02d}V{version:02d}"
#             paper_detail = QuestionPaperDetails(
#                 qpd_paper_id=paper_id,
#                 qpd_q_codes=shuffled_questions,
#                 qpd_total_time=payload.total_time,
#                 qpd_total_questions=payload.total_questions,
#                 qpd_design_name=payload.exam_name,
#                 qpd_design_id=new_design.id,
#                 created_by=current_user.id
#             )
#             db.add(paper_detail)

#     await db.commit()

#     # ----------------------------------------------------------
#     # Fetch Created Papers
#     # ----------------------------------------------------------
#     papers_result = await db.execute(
#         select(QuestionPaperDetails).where(QuestionPaperDetails.qpd_design_id == new_design.id)
#     )
#     papers = papers_result.scalars().all()

#     # ----------------------------------------------------------
#     # Collect Question Codes
#     # ----------------------------------------------------------
#     all_codes_in_papers = set(code for paper in papers for code in paper.qpd_q_codes)

#     questions_result = await db.execute(
#         select(Questions).where(Questions.qmt_question_code.in_(all_codes_in_papers))
#     )
#     questions_list = questions_result.scalars().all()
#     questions_map = {q.qmt_question_code: q for q in questions_list}

#     # ----------------------------------------------------------
#     # Build Question Papers Response
#     # ----------------------------------------------------------
#     question_papers_response = []

#     for paper in papers:
#         qns_list = []
#         for code in paper.qpd_q_codes:
#             q = questions_map.get(code)
#             if not q:
#                 continue

#             options_list = build_options(q, include_answers=include_correct_answers)

#             qns_list.append({
#                 "id": q.qmt_question_code,
#                 "text": q.qmt_question_text,
#                 "options": options_list
#             })

#         question_papers_response.append({
#             "id": paper.qpd_paper_id,
#             "qns": qns_list
#         })

#     # ----------------------------------------------------------
#     # Return Final Response
#     # ----------------------------------------------------------
#     return {
#         "exam_name": new_design.dm_design_name,
#         "exam_code": new_design.dm_design_code,
#         "number_of_sets": new_design.dm_no_of_sets,
#         "number_of_versions": new_design.dm_no_of_versions,
#         "no_of_qns": new_design.dm_total_questions,
#         "subject": subject_obj.smt_subject_name,
#         "medium": medium_obj.mmt_medium_name,
#         "exam_type": exam_type_obj.qtm_type_name,
#         "question_papers": question_papers_response
#     }




# @router.get(
#     "/v1/exams",
#     response_model=DesignPaperListResponse,
#     tags=["Exam History"]
# )
# async def list_all_question_papers(
#     db: AsyncSession = Depends(get_db),
#     current_user: user.User = Depends(get_current_user)
# ):
#     """
#     Lists Designs and their Question Papers.
#     Admins see all Designs.
#     Other users see only their own Designs.
#     """

#     # Determine if current_user is admin
#     role_stmt = select(Role).where(Role.id == current_user.role_id)
#     result = await db.execute(role_stmt)
#     role_obj = result.scalar_one_or_none()

#     if not role_obj:
#         raise HTTPException(status_code=403, detail="User role not found")

#     is_admin = role_obj.role_code == "100"

#     # Fetch Designs
#     if is_admin:
#         design_stmt = select(Design)
#     else:
#         design_stmt = select(Design).where(Design.created_by == current_user.id)

#     result = await db.execute(design_stmt)
#     designs = result.scalars().all()

#     if not designs:
#         return {"designs": []}

#     response_designs = []

#     for design in designs:
#         # Fetch Subject
#         subject_name = "Unknown"
#         subject_result = await db.execute(select(Subject).where(Subject.id == design.dm_subject_id))
#         subject = subject_result.scalar_one_or_none()
#         if subject:
#             subject_name = subject.smt_subject_name

#         # Fetch Medium
#         medium_name = "Unknown"
#         medium_result = await db.execute(select(Medium).where(Medium.id == design.dm_medium_id))
#         medium = medium_result.scalar_one_or_none()
#         if medium:
#             medium_name = medium.mmt_medium_name

#         # Fetch Exam Type
#         exam_type_name = "Unknown"
#         exam_type_result = await db.execute(select(Question_Type).where(Question_Type.id == design.dm_exam_type_id))
#         exam_type = exam_type_result.scalar_one_or_none()
#         if exam_type:
#             exam_type_name = exam_type.qtm_type_name

#         # Fetch Question Papers for this Design
#         # paper_result = await db.execute(
#         #     select(QuestionPaperDetails.qpd_paper_id)
#         #     .where(QuestionPaperDetails.qpd_design_id == design.id)
#         # )
#         # paper_codes = paper_result.scalars().all()

#         response_designs.append({
#             "exam_name": design.dm_design_name,
#             "exam_code": design.dm_design_code,
#             "exam_type": exam_type_name,
#             "exam_mode": design.dm_exam_mode,
#             "standard": design.dm_standard,
#             "subject": subject_name,
#             "medium": medium_name,
#             "status": design.dm_status,
#             "number_of_sets": design.dm_no_of_sets,
#             "number_of_versions": design.dm_no_of_versions,
#             "total_questions": design.dm_total_questions,
#         })

#     return {"exams": response_designs}

# @router.get(
#     "/v1/exams/{exam_code}",
#     response_model=SingleDesignResponse,
#     tags=["Exam History"]
# )
# async def get_exam_by_code(
#     exam_code: str,
#     db: AsyncSession = Depends(get_db),
#     current_user: user.User = Depends(get_current_user)
# ):
#     """
#     Get single exam design with its question papers using exam_code
#     """

#     # Determine user role
#     role_stmt = select(Role).where(Role.id == current_user.role_id)
#     result = await db.execute(role_stmt)
#     role_obj = result.scalar_one_or_none()

#     if not role_obj:
#         raise HTTPException(status_code=403, detail="User role not found")

#     is_admin = role_obj.role_code == "100"

#     # Query for the design with the given code
#     stmt = select(Design).where(Design.dm_design_code == exam_code)
#     if not is_admin:
#         stmt = stmt.where(Design.created_by == current_user.id)

#     result = await db.execute(stmt)
#     design = result.scalar_one_or_none()

#     if not design:
#         raise HTTPException(status_code=404, detail="Design not found")

#     # Fetch related data
#     subject_result = await db.execute(select(Subject).where(Subject.id == design.dm_subject_id))
#     subject = subject_result.scalar_one_or_none()
#     subject_name = subject.smt_subject_name if subject else "Unknown"

#     medium_result = await db.execute(select(Medium).where(Medium.id == design.dm_medium_id))
#     medium = medium_result.scalar_one_or_none()
#     medium_name = medium.mmt_medium_name if medium else "Unknown"

#     exam_type_result = await db.execute(select(Question_Type).where(Question_Type.id == design.dm_exam_type_id))
#     exam_type = exam_type_result.scalar_one_or_none()
#     exam_type_name = exam_type.qtm_type_name if exam_type else "Unknown"

#     # Get paper codes
#     paper_result = await db.execute(
#         select(QuestionPaperDetails.qpd_paper_id).where(QuestionPaperDetails.qpd_design_id == design.id)
#     )
#     paper_codes = paper_result.scalars().all()

#     return {
#         "design": {
#             "exam_name": design.dm_design_name,
#             "exam_code": design.dm_design_code,
#             "exam_type": exam_type_name,
#             "exam_mode": design.dm_exam_mode,
#             "standard": design.dm_standard,
#             "subject": subject_name,
#             "medium": medium_name,
#             "status": design.dm_status,
#             "number_of_sets": design.dm_no_of_sets,
#             "number_of_versions": design.dm_no_of_versions,
#             "total_questions": design.dm_total_questions,
#             "papers": paper_codes
#         }
#     }

# @router.delete("/v1/exams/{exam_code}", 
#                     status_code=status.HTTP_200_OK,
#                     tags=["Delete Exams"])
# async def delete__by_code(
#     exam_code: str,
#     db: AsyncSession = Depends(get_db),
#     current_user: user.User = Depends(get_current_user)
# ):
#     """Delete a design by exam code. Only admin or creator can delete."""
    
#     # Fetch user role
#     role_stmt = select(Role).where(Role.id == current_user.role_id)
#     result = await db.execute(role_stmt)
#     role_obj = result.scalar_one_or_none()

#     if not role_obj:
#         raise HTTPException(status_code=403, detail="User role not found")

#     is_admin = role_obj.role_code == "100"

#     # Fetch design with authorization logic
#     stmt = select(Design).where(Design.dm_design_code == exam_code)
#     if not is_admin:
#         stmt = stmt.where(Design.created_by == current_user.id)

#     result = await db.execute(stmt)
#     design = result.scalar_one_or_none()

#     if not design:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Exam Code not found or you do not have permission to delete it"
#         )

#     # Proceed to delete
#     await db.delete(design)
#     await db.commit()

#     return {"message": f"Exam with code '{exam_code}' deleted successfully."}


# @router.delete("/v1/qn_papers/{paper_code}", 
#                status_code=status.HTTP_200_OK,
#                tags=["Delete QPs"])
# async def delete_question_paper_by_code(
#     paper_code: str,
#     db: AsyncSession = Depends(get_db),
#     current_user: user.User = Depends(get_current_user)
# ):
#     """Delete a question paper by paper code. Only admin or creator can delete."""

#     # Get the user role
#     role_stmt = select(Role).where(Role.id == current_user.role_id)
#     result = await db.execute(role_stmt)
#     role_obj = result.scalar_one_or_none()

#     if not role_obj:
#         raise HTTPException(status_code=403, detail="User role not found")

#     is_admin = role_obj.role_code == "100"

#     # Fetch the question paper with authorization logic
#     stmt = select(QuestionPaperDetails).where(QuestionPaperDetails.qpd_paper_id == paper_code)
#     if not is_admin:
#         stmt = stmt.where(QuestionPaperDetails.created_by == current_user.id)

#     result = await db.execute(stmt)
#     paper = result.scalar_one_or_none()

#     if not paper:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Question paper not found or you do not have permission to delete it"
#         )

#     # Delete it
#     await db.delete(paper)
#     await db.commit()

#     return {"message": f"Question paper with code '{paper_code}' deleted successfully."}

# @router.get(
#     "/v1/qn_papers/{paper_code}",
#     tags=["View/Print QPs"]
# )
# async def get_question_paper_by_id(
#     paper_id: str,
#     format: str = Query("json", enum=["json", "pdf"]),
#     db: AsyncSession = Depends(get_db),
#     current_user: user.User = Depends(get_current_user)
# ):
#     # Role check
#     role_stmt = select(Role).where(Role.id == current_user.role_id)
#     result = await db.execute(role_stmt)
#     role_obj = result.scalar_one_or_none()
#     if not role_obj:
#         raise HTTPException(status_code=403, detail="User role not found")
#     include_answers = role_obj.role_code == "100"

#     # Paper fetch
#     paper_stmt = select(QuestionPaperDetails).where(
#         QuestionPaperDetails.qpd_paper_id == paper_id,
#         *( [] if include_answers else [QuestionPaperDetails.created_by == current_user.id] )
#     )
#     result = await db.execute(paper_stmt)
#     paper = result.scalar_one_or_none()
#     if not paper:
#         raise HTTPException(status_code=404, detail="Question Paper not found.")

#     # Design fetch
#     design_result = await db.execute(select(Design).where(Design.id == paper.qpd_design_id))
#     design = design_result.scalar_one_or_none()
#     if not design:
#         raise HTTPException(status_code=404, detail="Design not found.")

#     # Helper for names
#     async def get_name(table, id_field, id_value, name_field):
#         stmt = select(table).where(id_field == id_value)
#         result = await db.execute(stmt)
#         obj = result.scalar_one_or_none()
#         return getattr(obj, name_field, "Unknown") if obj else "Unknown"

#     subject_name = await get_name(Subject, Subject.id, design.dm_subject_id, "smt_subject_name")
#     medium_name = await get_name(Medium, Medium.id, design.dm_medium_id, "mmt_medium_name")
#     exam_type_name = await get_name(Question_Type, Question_Type.id, design.dm_exam_type_id, "qtm_type_name")

#     # Questions
#     question_codes = paper.qpd_q_codes or []
#     questions_result = await db.execute(select(Questions).where(Questions.qmt_question_code.in_(question_codes)))
#     questions = questions_result.scalars().all()
#     questions_map = {q.qmt_question_code: q for q in questions}

#     # Build question list with correct option filtering
#     qns_list = []
#     for code in paper.qpd_q_codes:
#         q = questions_map.get(code)
#         if not q:
#             continue

#         opts = build_options(q, include_answers=include_answers)

#         if not include_answers:
#             # Ensure is_correct is *completely* stripped out
#             for o in opts:
#                 o.pop("is_correct", None)

#         options_objs = [OptionResponseEach(**opt) for opt in opts]
#         qns_list.append(QuestionResponseEach(
#             id=q.qmt_question_code,
#             text=q.qmt_question_text,
#             options=options_objs
#         ))

#     # Build JSON response
#     response_data = QuestionPaperResponseEach(
#         id=paper.qpd_paper_id,
#         exam_name=design.dm_design_name,
#         design_id=design.id,
#         number_of_sets=design.dm_no_of_sets,
#         number_of_versions=design.dm_no_of_versions,
#         no_of_qns=design.dm_total_questions,
#         subject=subject_name,
#         medium=medium_name,
#         exam_type=exam_type_name,
#         standard=design.dm_standard,
#         qns=qns_list
#     )

#     if format == "json":
#         return JSONResponse(content=response_data.dict(exclude_none=True))

#     elif format == "pdf":
#         buffer = BytesIO()
#         pdf = canvas.Canvas(buffer)
#         pdf.setTitle(f"Question Paper {paper.qpd_paper_id}")
#         pdf.drawString(100, 800, f"Exam Name: {design.dm_design_name}")
#         pdf.drawString(100, 780, f"Paper ID: {paper.qpd_paper_id}")
#         pdf.drawString(100, 760, f"Subject: {subject_name}")
#         pdf.drawString(100, 740, f"Medium: {medium_name}")
#         pdf.drawString(100, 720, f"Exam Type: {exam_type_name}")
#         y = 700
#         for idx, question in enumerate(qns_list, start=1):
#             pdf.drawString(100, y, f"Q{idx}: {question.text}")
#             y -= 20
#             correct_option_id = None
#             for opt in question.options:
#                 pdf.drawString(120, y, f"{opt.id}. {opt.text}")
#                 if include_answers and hasattr(opt, "is_correct") and opt.is_correct:
#                     correct_option_id = opt.id
#                 y -= 20

#             if include_answers and correct_option_id:
#                 pdf.drawString(120, y, f"correct answer: {correct_option_id}")
#                 y -= 20

#             y -= 10
#             if y < 100:
#                 pdf.showPage()
#                 y = 800
#         pdf.showPage()
#         pdf.save()
#         buffer.seek(0)
#         return StreamingResponse(
#             buffer,
#             media_type="application/pdf",
#             headers={"Content-Disposition": f"attachment; filename={paper.qpd_paper_id}.pdf", "Content-Type": "application/pdf"}
#         )
#     else:
#         raise HTTPException(status_code=400, detail="Invalid format. Use ?format=json or ?format=pdf")
    
# @router.get(
#     "/v1/admin/qn_papers/{paper_code}",
#     tags=["Admin View/Print QPs"]
# )
# async def admin_get_question_paper_by_id(
#     paper_id: str,
#     format: str = Query("json", enum=["json", "pdf"]),
#     questions_only: bool = Query(False, description="If true, hides answers even for admin"),
#     db: AsyncSession = Depends(get_db),
#     current_user: user.User = Depends(get_current_user)
# ):
#     """
#     Admin-only endpoint to view or print a question paper.
#     Supports ?questions_only=true to suppress answers even for admin.
#     """

#     # Check role
#     role_stmt = select(Role).where(Role.id == current_user.role_id)
#     result = await db.execute(role_stmt)
#     role_obj = result.scalar_one_or_none()
#     if not role_obj:
#         raise HTTPException(status_code=403, detail="User role not found")
#     if role_obj.role_code != "100":
#         raise HTTPException(status_code=403, detail="Only admin can access this endpoint")

#     # Paper fetch (admins can see all)
#     paper_stmt = select(QuestionPaperDetails).where(QuestionPaperDetails.qpd_paper_id == paper_id)
#     result = await db.execute(paper_stmt)
#     paper = result.scalar_one_or_none()
#     if not paper:
#         raise HTTPException(status_code=404, detail="Question Paper not found.")

#     # Design fetch
#     design_result = await db.execute(select(Design).where(Design.id == paper.qpd_design_id))
#     design = design_result.scalar_one_or_none()
#     if not design:
#         raise HTTPException(status_code=404, detail="Design not found.")

#     # Helper for names
#     async def get_name(table, id_field, id_value, name_field):
#         stmt = select(table).where(id_field == id_value)
#         result = await db.execute(stmt)
#         obj = result.scalar_one_or_none()
#         return getattr(obj, name_field, "Unknown") if obj else "Unknown"

#     subject_name = await get_name(Subject, Subject.id, design.dm_subject_id, "smt_subject_name")
#     medium_name = await get_name(Medium, Medium.id, design.dm_medium_id, "mmt_medium_name")
#     exam_type_name = await get_name(Question_Type, Question_Type.id, design.dm_exam_type_id, "qtm_type_name")

#     # Questions
#     question_codes = paper.qpd_q_codes or []
#     questions_result = await db.execute(select(Questions).where(Questions.qmt_question_code.in_(question_codes)))
#     questions = questions_result.scalars().all()
#     questions_map = {q.qmt_question_code: q for q in questions}

#     # Include answers unless questions_only is true
#     include_answers = not questions_only

#     qns_list = []
#     for code in paper.qpd_q_codes:
#         q = questions_map.get(code)
#         if not q:
#             continue

#         opts = build_options(q, include_answers=include_answers)

#         if questions_only:
#             # Strip is_correct completely
#             for o in opts:
#                 o.pop("is_correct", None)

#         options_objs = [OptionResponseEach(**opt) for opt in opts]
#         qns_list.append(QuestionResponseEach(
#             id=q.qmt_question_code,
#             text=q.qmt_question_text,
#             options=options_objs
#         ))

#     # Build JSON response
#     response_data = QuestionPaperResponseEach(
#         id=paper.qpd_paper_id,
#         exam_name=design.dm_design_name,
#         design_id=design.id,
#         number_of_sets=design.dm_no_of_sets,
#         number_of_versions=design.dm_no_of_versions,
#         no_of_qns=design.dm_total_questions,
#         subject=subject_name,
#         medium=medium_name,
#         exam_type=exam_type_name,
#         standard=design.dm_standard,
#         qns=qns_list
#     )

#     if format == "json":
#         return JSONResponse(content=response_data.dict(exclude_none=True))

#     elif format == "pdf":
#         buffer = BytesIO()
#         pdf = canvas.Canvas(buffer)
#         pdf.setTitle(f"Question Paper {paper.qpd_paper_id}")
#         pdf.drawString(100, 800, f"Exam Name: {design.dm_design_name}")
#         pdf.drawString(100, 780, f"Paper ID: {paper.qpd_paper_id}")
#         pdf.drawString(100, 760, f"Subject: {subject_name}")
#         pdf.drawString(100, 740, f"Medium: {medium_name}")
#         pdf.drawString(100, 720, f"Exam Type: {exam_type_name}")
#         y = 700

#         for idx, question in enumerate(qns_list, start=1):
#             pdf.drawString(100, y, f"Q{idx}: {question.text}")
#             y -= 20

#             correct_option_id = None
#             for opt in question.options:
#                 pdf.drawString(120, y, f"{opt.id}. {opt.text}")
#                 if include_answers and hasattr(opt, "is_correct") and opt.is_correct:
#                     correct_option_id = opt.id
#                 y -= 20

#             if include_answers and correct_option_id:
#                 pdf.drawString(120, y, f"correct answer: {correct_option_id}")
#                 y -= 20

#             y -= 10
#             if y < 100:
#                 pdf.showPage()
#                 y = 800

#         pdf.showPage()
#         pdf.save()
#         buffer.seek(0)
#         return StreamingResponse(
#             buffer,
#             media_type="application/pdf",
#             headers={"Content-Disposition": f"attachment; filename={paper.qpd_paper_id}.pdf", "Content-Type": "application/pdf"}
#         )
#     else:
#         raise HTTPException(status_code=400, detail="Invalid format. Use ?format=json or ?format=pdf")


# # @router.get(
# #     "/v1/question_papers/{paper_id}",
# #     response_model=QuestionPaperResponseEach,
# #     tags=["Question Paper History"]
# # )
# # async def get_question_paper_by_id(
# #     paper_id: str,
# #     db: AsyncSession = Depends(get_db),
# #     current_user: user.User = Depends(get_current_user)
# # ):
# #     """
# #     Fetch a single question paper by paper_id.
# #     - Admin can fetch any paper
# #     - Non-admin can fetch only papers they created
# #     """

# #     # Determine user role
# #     role_stmt = select(Role).where(Role.id == current_user.role_id)
# #     result = await db.execute(role_stmt)
# #     role_obj = result.scalar_one_or_none()

# #     if not role_obj:
# #         raise HTTPException(status_code=403, detail="User role not found")

# #     is_admin = role_obj.role_code == "100"

# #     # Fetch the question paper, with access control
# #     if is_admin:
# #         paper_stmt = select(QuestionPaperDetails).where(QuestionPaperDetails.qpd_paper_id == paper_id)
# #     else:
# #         paper_stmt = select(QuestionPaperDetails).where(
# #             and_(
# #                 QuestionPaperDetails.qpd_paper_id == paper_id,
# #                 QuestionPaperDetails.created_by == current_user.id
# #             )
# #         )

# #     result = await db.execute(paper_stmt)
# #     paper = result.scalar_one_or_none()
# #     if not paper:
# #         raise HTTPException(status_code=404, detail="Question Paper not found.")

# #     # Fetch related Design
# #     design_stmt = select(Design).where(Design.id == paper.qpd_design_id)
# #     result = await db.execute(design_stmt)
# #     design = result.scalar_one_or_none()
# #     if not design:
# #         raise HTTPException(status_code=404, detail="Design not found.")

# #     # Resolve Subject, Medium, Exam Type names
# #     subject_name = "Unknown"
# #     medium_name = "Unknown"
# #     exam_type_name = "Unknown"

# #     subject_result = await db.execute(select(Subject).where(Subject.id == design.dm_subject_id))
# #     subject = subject_result.scalar_one_or_none()
# #     if subject:
# #         subject_name = subject.smt_subject_name

# #     medium_result = await db.execute(select(Medium).where(Medium.id == design.dm_medium_id))
# #     medium = medium_result.scalar_one_or_none()
# #     if medium:
# #         medium_name = medium.mmt_medium_name

# #     exam_type_result = await db.execute(select(Question_Type).where(Question_Type.id == design.dm_exam_type_id))
# #     exam_type = exam_type_result.scalar_one_or_none()
# #     if exam_type:
# #         exam_type_name = exam_type.qtm_type_name

# #     # Fetch Questions in this paper
# #     question_codes = paper.qpd_q_codes or []
# #     if not question_codes:
# #         question_codes = []

# #     questions_stmt = select(Questions).where(Questions.qmt_question_code.in_(question_codes))
# #     result = await db.execute(questions_stmt)
# #     questions = result.scalars().all()

# #     qns_list = []
# #     for q in questions:
# #         # Build options, only admins see is_correct
# #         options = [
# #             OptionResponseEach(id="A", text=q.qmt_option1, is_correct=(q.qmt_correct_answer == "option A" if is_admin else None)),
# #             OptionResponseEach(id="B", text=q.qmt_option2, is_correct=(q.qmt_correct_answer == "option B" if is_admin else None)),
# #             OptionResponseEach(id="C", text=q.qmt_option3, is_correct=(q.qmt_correct_answer == "option C" if is_admin else None)),
# #             OptionResponseEach(id="D", text=q.qmt_option4, is_correct=(q.qmt_correct_answer == "option D" if is_admin else None)),
# #         ]

# #         qns_list.append(
# #             QuestionResponseEach(
# #                 id=q.qmt_question_code,
# #                 text=q.qmt_question_text,
# #                 options=options
# #             )
# #         )

# #     #  Build and return the final response
# #     response = QuestionPaperResponseEach(
# #         id=paper.qpd_paper_id,
# #         exam_name=design.dm_design_name,
# #         design_id=design.id,
# #         number_of_sets=design.dm_no_of_sets,
# #         number_of_versions=design.dm_no_of_versions,
# #         no_of_qns=design.dm_total_questions,
# #         subject=subject_name,
# #         medium=medium_name,
# #         exam_type=exam_type_name,
# #         standard=design.dm_standard,
# #         qns=qns_list
# #     )

# #     return response



        
    














