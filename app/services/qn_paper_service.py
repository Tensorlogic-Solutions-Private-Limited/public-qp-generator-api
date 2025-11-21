from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from typing import Optional, List, Tuple

from app.models.master import Design, Subject, Medium, Question_Type, Questions, Taxonomy
from app.models.user import Role, User
from app.models.master import Design, Subject, Medium, Question_Type, QuestionPaperDetails
from app.schemas.qn_papers import SingleDesignResponse, SingleDesignResponseItem, DesignPaperListResponseItem,DesignPaperListResponsePaginated

from app.utils.get_user_role import get_user_role
from app.utils.get_name import get_name

from sqlalchemy import select, func, and_
from sqlalchemy.orm import joinedload
from typing import Optional, List
from datetime import date

async def get_all_exam_designs(
    db: AsyncSession,
    current_user: User,
    status: str,
    exam_name: Optional[str] = None,
    subject: Optional[str] = None,
    medium: Optional[str] = None,
    standard: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    page: int = 1,
    limit: int = 20
) -> Tuple[List[dict], int]:
    """Fetches paginated exam designs with filters for admins and regular users."""

    # Validate status
    if status not in ["draft", "closed"]:
        raise HTTPException(status_code=400, detail="Invalid status. Must be 'draft' or 'closed'.")

    # Role validation
    role_obj = await get_user_role(db, current_user.role_id)
    if not role_obj:
        raise HTTPException(status_code=404, detail="User role not found")
    is_admin = role_obj.role_code == "100"

    # Base query (designs only)
    query = (
        select(Design)
        .where(Design.dm_status == status)
        .options(
            joinedload(Design.subject),
            joinedload(Design.medium),
            joinedload(Design.type)
        )
    )

    # Restrict to user's own designs if not admin
    if not is_admin:
        query = query.where(Design.created_by == current_user.id)

    # Dynamic filters
    filters = []
    if exam_name:
        filters.append(Design.dm_design_name.ilike(f"%{exam_name}%"))
    if subject:
        filters.append(Design.subject.has(Subject.smt_subject_name == subject))
    if medium:
        filters.append(Design.medium.has(Medium.mmt_medium_name == medium))
    if standard:
        filters.append(Design.dm_standard == standard)
    if start_date and end_date:
        filters.append(func.date(Design.created_at).between(start_date, end_date))
    elif start_date:
        filters.append(func.date(Design.created_at) >= start_date)
    elif end_date:
        filters.append(func.date(Design.created_at) <= end_date)

    if filters:
        query = query.where(and_(*filters))

    query = query.order_by(Design.created_at.desc())

    # Count query for pagination
    count_query = select(func.count()).select_from(query.subquery())
    total_count = (await db.execute(count_query)).scalar()

    # Paginated fetch
    query = query.limit(limit).offset((page - 1) * limit)
    result = await db.execute(query)
    designs = result.scalars().all()

    # Construct response dicts manually (no Pydantic)
    response_designs = []
    for d in designs:
        response_designs.append({
            "exam_name": d.dm_design_name,
            "exam_code": d.dm_design_code,
            "exam_type": d.type.qtm_type_name if d.type else None,
            "exam_mode": d.dm_exam_mode or None,
            "standard": d.dm_standard or None,
            "subject": d.subject.smt_subject_name if d.subject else None,
            "medium": d.medium.mmt_medium_name if d.medium else None,
            "status": d.dm_status,
            "number_of_sets": d.dm_no_of_sets,
            "number_of_versions": d.dm_no_of_versions,
            "total_questions": d.dm_total_questions,
            "created_at": d.created_at.isoformat() if d.created_at else None,  # ✅ Convert datetime to string
            "created_by": await get_name(db, User, User.id, d.created_by, "username"),
            "created_by_id": d.created_by,
        })

    return response_designs, total_count

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from fastapi import HTTPException, status

async def get_design_by_exam_code(
    db: AsyncSession,
    exam_code: str,
    current_user: User
) -> dict:
    # Get user role
    role_obj = await get_user_role(db, current_user.role_id)
    if not role_obj:
        raise HTTPException(status_code=404, detail="User role not found")

    is_admin = role_obj.role_code == "100"

    # Get design
    stmt = select(Design).where(Design.dm_design_code == exam_code)
    if not is_admin:
        stmt = stmt.where(Design.created_by == current_user.id)

    result = await db.execute(stmt)
    design = result.scalar_one_or_none()
    if not design:
        raise HTTPException(status_code=404, detail="Design not found")

    # Lookup values
    subject_name = (await db.execute(
        select(Subject.smt_subject_name).where(Subject.id == design.dm_subject_id)
    )).scalar_one_or_none() or "Unknown"

    medium_name = (await db.execute(
        select(Medium.mmt_medium_name).where(Medium.id == design.dm_medium_id)
    )).scalar_one_or_none() or "Unknown"

    exam_type_name = (await db.execute(
        select(Question_Type.qtm_type_name).where(Question_Type.id == design.dm_exam_type_id)
    )).scalar_one_or_none() or "Unknown"

    # Paper codes
    paper_codes = (await db.execute(
        select(QuestionPaperDetails.qpd_paper_id)
        .where(QuestionPaperDetails.qpd_design_id == design.id)
    )).scalars().all()

    # Questions to exclude
    qtn_codes_to_exclude = []
    codes_list = design.dm_questions_to_exclude or []

    if codes_list:
        result = await db.execute(
            select(
                Questions.qmt_question_code,
                Questions.qmt_question_text,
                Taxonomy.stm_chapter_code,
                Taxonomy.stm_chapter_name,
                Taxonomy.stm_topic_code,
                Taxonomy.stm_topic_name
            )
            .join(Taxonomy, Questions.qmt_taxonomy_id == Taxonomy.id)
            .where(Questions.qmt_question_code.in_(codes_list))
        )

        for code, txt, ch_code, ch_name, t_code, t_name in result.all():
            qtn_codes_to_exclude.append({
                "code": code,
                "txt": txt,
                "chapter_details": {"code": ch_code, "name": ch_name},
                "topic_details": {"code": t_code, "name": t_name}
            })

    # Resolve chapter/topic groups
    raw_chapters_topics = design.dm_chapter_topics or []
    resolved_chapters_topics = []

    for group in raw_chapters_topics:
        group_type = group.get("type")
        codes = group.get("codes", [])
        code_values = [item["code"] for item in codes]
        resolved_codes = []

        if group_type == "chapter":
            result = await db.execute(
                select(Taxonomy.stm_chapter_code, Taxonomy.stm_chapter_name)
                .where(Taxonomy.stm_chapter_code.in_(code_values))
                .distinct()
            )
            name_map = {code: name for code, name in result.all()}

            for item in codes:
                resolved_codes.append({
                    "code": item["code"],
                    "qn_count": item.get("qn_count"),
                    "name": name_map.get(item["code"], "Unknown")
                    # No chapter_details included for chapters
                })

        elif group_type == "topic":
            result = await db.execute(
                select(
                    Taxonomy.stm_topic_code,
                    Taxonomy.stm_topic_name,
                    Taxonomy.stm_chapter_code,
                    Taxonomy.stm_chapter_name
                )
                .where(Taxonomy.stm_topic_code.in_(code_values))
                .distinct()
            )
            topic_map = {
                code: {
                    "name": name,
                    "chapter_details": {
                        "code": ch_code,
                        "name": ch_name
                    }
                }
                for code, name, ch_code, ch_name in result.all()
            }

            for item in codes:
                topic_data = topic_map.get(item["code"], {})
                resolved_code = {
                    "code": item["code"],
                    "qn_count": item.get("qn_count"),
                    "name": topic_data.get("name", "Unknown"),
                }

                if "chapter_details" in topic_data:
                    resolved_code["chapter_details"] = topic_data["chapter_details"]

                resolved_codes.append(resolved_code)

        resolved_chapters_topics.append({
            "type": group_type,
            "codes": resolved_codes
        })

    # Final response
    response_model = SingleDesignResponse(
        design=SingleDesignResponseItem(
            exam_name=design.dm_design_name,
            exam_code=design.dm_design_code,
            exam_type=exam_type_name,
            exam_mode=design.dm_exam_mode,
            standard=design.dm_standard,
            subject=subject_name,
            medium=medium_name,
            status=design.dm_status,
            number_of_sets=design.dm_no_of_sets,
            number_of_versions=design.dm_no_of_versions,
            total_questions=design.dm_total_questions,
            qtn_codes_to_exclude=qtn_codes_to_exclude,
            chapters_topics=resolved_chapters_topics,
            papers=paper_codes
        )
    )

    return response_model.model_dump(exclude_none=False)


# async def get_design_by_exam_code(
#     db: AsyncSession,
#     exam_code: str,
#     current_user: User
# ) -> SingleDesignResponse:

#     # Get user role
#     role_obj = await get_user_role(db, current_user.role_id)
#     if not role_obj:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User role not found")

#     is_admin = role_obj.role_code == "100"

#     # Get design
#     design_stmt = select(Design).where(Design.dm_design_code == exam_code)
#     if not is_admin:
#         design_stmt = design_stmt.where(Design.created_by == current_user.id)

#     design_result = await db.execute(design_stmt)
#     design = design_result.scalar_one_or_none()
#     if not design:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Design not found")

#     # Subject
#     subject_name = (await db.execute(
#         select(Subject.smt_subject_name).where(Subject.id == design.dm_subject_id)
#     )).scalar_one_or_none() or "Unknown"

#     # Medium
#     medium_name = (await db.execute(
#         select(Medium.mmt_medium_name).where(Medium.id == design.dm_medium_id)
#     )).scalar_one_or_none() or "Unknown"

#     # Exam type
#     exam_type_name = (await db.execute(
#         select(Question_Type.qtm_type_name).where(Question_Type.id == design.dm_exam_type_id)
#     )).scalar_one_or_none() or "Unknown"

#     # Paper codes
#     paper_codes = (await db.execute(
#         select(QuestionPaperDetails.qpd_paper_id).where(QuestionPaperDetails.qpd_design_id == design.id)
#     )).scalars().all()

#     # Questions to exclude
#     qtn_codes_to_exclude = []
#     codes_list = design.dm_questions_to_exclude or []

#     if codes_list:
#         q_texts_result = await db.execute(
#             select(
#                 Questions.qmt_question_code,
#                 Questions.qmt_question_text,
#                 Taxonomy.stm_chapter_code,
#                 Taxonomy.stm_chapter_name,
#                 Taxonomy.stm_topic_code,
#                 Taxonomy.stm_topic_name
#             )
#             .join(Taxonomy, Questions.qmt_taxonomy_id == Taxonomy.id)
#             .where(Questions.qmt_question_code.in_(codes_list))
#         )
#         question_info = q_texts_result.all()

#         question_info_map = {
#             code: {
#                 "txt": txt,
#                 "chapter_details": {
#                     "code": ch_code,
#                     "name": ch_name
#                 },
#                 "topic_details": {
#                     "code": t_code,
#                     "name": t_name
#                 }
#             }
#             for code, txt, ch_code, ch_name, t_code, t_name in question_info
#         }

#         for code in codes_list:
#             info = question_info_map.get(code)
#             if info:
#                 qtn_codes_to_exclude.append({
#                     "code": code,
#                     "txt": info["txt"],
#                     "chapter_details": info["chapter_details"],
#                     "topic_details": info["topic_details"]
#                 })

#     # Resolve chapters_topics with names
#     raw_chapters_topics = design.dm_chapter_topics or []
#     resolved_chapters_topics = []

#     for group in raw_chapters_topics:
#         group_type = group.get("type")
#         codes = group.get("codes", [])
#         code_values = [item["code"] for item in codes]
#         resolved_codes = []

#         if group_type == "chapter":
#             result = await db.execute(
#                 select(Taxonomy.stm_chapter_code, Taxonomy.stm_chapter_name)
#                 .where(Taxonomy.stm_chapter_code.in_(code_values))
#                 .distinct()
#             )
#             name_map = {code: name for code, name in result.all()}

#         elif group_type == "topic":
#             result = await db.execute(
#                 select(Taxonomy.stm_topic_code, Taxonomy.stm_topic_name)
#                 .where(Taxonomy.stm_topic_code.in_(code_values))
#                 .distinct()
#             )
#             name_map = {code: name for code, name in result.all()}

#         else:
#             name_map = {}

#         for item in codes:
#             resolved_codes.append({
#                 "code": item["code"],
#                 "qn_count": item.get("qn_count", 0),
#                 "name": name_map.get(item["code"], "Unknown")
#             })

#         resolved_chapters_topics.append({
#             "type": group_type,
#             "codes": resolved_codes
#         })

#     # Final response
#     return SingleDesignResponse(
#         design=SingleDesignResponseItem(
#             exam_name=design.dm_design_name,
#             exam_code=design.dm_design_code,
#             exam_type=exam_type_name,
#             exam_mode=design.dm_exam_mode,
#             standard=design.dm_standard,
#             subject=subject_name,
#             medium=medium_name,
#             status=design.dm_status,
#             number_of_sets=design.dm_no_of_sets,
#             number_of_versions=design.dm_no_of_versions,
#             total_questions=design.dm_total_questions,
#             qtn_codes_to_exclude=qtn_codes_to_exclude,
#             chapters_topics=resolved_chapters_topics,
#             papers=paper_codes
#         )
#     )
async def delete_design_by_exam_code(
    db: AsyncSession,
    current_user: User,
    exam_code: str
) -> str:
    # Get user role
    role_obj = await get_user_role(db,current_user.role_id)

    if not role_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="User role not found")

    is_admin = role_obj.role_code == "100"

    # Fetch design with permission check
    stmt = select(Design).where(Design.dm_design_code == exam_code)
    if not is_admin:
        stmt = stmt.where(Design.created_by == current_user.id)

    result = await db.execute(stmt)
    design = result.scalar_one_or_none()

    if not design:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam code not found or you do not have permission to delete it"
        )

    await db.delete(design)
    await db.commit()

    return f"Exam with code '{exam_code}' deleted successfully."

async def delete_question_paper_by_code(
    db: AsyncSession,
    current_user: User,
    paper_code: str
) -> str:
    # Get the user's role

    role_obj = await get_user_role(db,current_user.role_id)

    if not role_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="User role not found"
        )

    is_admin = role_obj.role_code == "100"

    # Fetch the question paper
    stmt = select(QuestionPaperDetails).where(QuestionPaperDetails.qpd_paper_id == paper_code)
    if not is_admin:
        stmt = stmt.where(QuestionPaperDetails.created_by == current_user.id)

    result = await db.execute(stmt)
    paper = result.scalar_one_or_none()

    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question paper not found or you do not have permission to delete it"
        )

    # Perform delete
    await db.delete(paper)
    await db.commit()

    return f"Question paper with code '{paper_code}' deleted successfully."