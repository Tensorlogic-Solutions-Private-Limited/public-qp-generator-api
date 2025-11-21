import random
from fastapi import HTTPException,status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime


from app.models.master import (
    Design,
    Questions,
    Question_Type,
    Subject,
    Medium,
    Taxonomy,
    QuestionPaperDetails
)
from app.models.user import Role
from app.utils.build_options import build_options
from app.schemas.exams import DesignBase,QuestionSelection,DesignCreate, DesignUpdate
from app.utils.get_user_role import get_user_role

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import random

from app.utils.exam_utils import (
    check_existing_design,
    resolve_foreign_keys,
    select_questions,
    generate_unique_design_code
)

from app.constants.status_codes import DESIGN_STATUS, DESIGN_STATUS_REVERSE

async def create_design_record(db: AsyncSession, payload, current_user, design_code, exam_type_obj, subject_obj, medium_obj, all_question_codes):
    new_design = Design(
        dm_design_name=payload.exam_name,
        dm_design_code=design_code,
        dm_exam_type_id=exam_type_obj.id,
        dm_exam_mode=payload.exam_mode,
        dm_total_time=payload.total_time,
        dm_total_questions=payload.total_questions,
        dm_no_of_versions=payload.no_of_versions,
        dm_no_of_sets=payload.no_of_sets,
        dm_subject_id=subject_obj.id,
        dm_medium_id=medium_obj.id,
        dm_standard=payload.standard,
        dm_status='closed',
        dm_total_question_codes=list(all_question_codes),
        created_by=current_user.id
    )
    db.add(new_design)
    await db.commit()
    await db.refresh(new_design)
    return new_design


async def create_question_paper_details(db: AsyncSession, design, selected_codes, payload, current_user):
    chunks = [
        selected_codes[i * payload.total_questions : (i + 1) * payload.total_questions]
        for i in range(payload.no_of_sets)
    ]
    for set_index, question_set in enumerate(chunks, start=1):
        for version in range(1, payload.no_of_versions + 1):
            shuffled = question_set.copy()
            random.shuffle(shuffled)
            paper_id = f"QP{design.id:02d}S{set_index:02d}V{version:02d}"
            db.add(QuestionPaperDetails(
                qpd_paper_id=paper_id,
                qpd_q_codes=shuffled,
                qpd_total_time=payload.total_time,
                qpd_total_questions=payload.total_questions,
                qpd_design_name=payload.exam_name,
                qpd_design_id=design.id,
                created_by=current_user.id
            ))
    await db.commit()


async def build_response(db: AsyncSession, design, include_answers):
    papers = (await db.execute(
        select(QuestionPaperDetails).where(QuestionPaperDetails.qpd_design_id == design.id)
    )).scalars().all()

    all_codes = set(code for paper in papers for code in paper.qpd_q_codes)
    questions_map = {
        q.qmt_question_code: q for q in (await db.execute(
            select(Questions).where(Questions.qmt_question_code.in_(all_codes))
        )).scalars().all()
    }

    response = []
    for paper in papers:
        qns = [
            {
                "id": q.qmt_question_code,
                "text": q.qmt_question_text,
                "options": build_options(q, include_answers)
            } for code in paper.qpd_q_codes if (q := questions_map.get(code))
        ]
        response.append({"id": paper.qpd_paper_id, "qns": qns})

    return response

async def create_exam_design_and_generate_qps(payload: DesignBase, current_user, db: AsyncSession):
    try:
        # Resolve user role for permissions
        role = await get_user_role(db, current_user.role_id)
        include_answers = role.role_code == "100"

        # Resolve foreign key references (exam type, subject, medium)
        exam_type_obj, subject_obj, medium_obj = await resolve_foreign_keys(db, payload)

        # Check for duplicate design name
        await check_existing_design(db, payload.exam_name)

        # Generate unique design code
        design_code = await generate_unique_design_code('EXM', db)

        # === 1. DRAFT SAVE (status=1) ===
        if payload.status == 1:
            design = await create_design_record(
                db=db,
                payload=payload,
                current_user=current_user,
                design_code=design_code,
                exam_type_obj=exam_type_obj,
                subject_obj=subject_obj,
                medium_obj=medium_obj,
                all_question_codes=[]  # Empty for draft
            )

            # Save optional fields for draft (serialize to JSON-compatible)
            design.dm_status = "draft"
            design.dm_chapter_topics = (
                [c.model_dump() for c in payload.chapters_topics] if payload.chapters_topics else None
            )
            design.dm_questions_to_exclude = payload.qtn_codes_to_exclude or None

            await db.commit()
            await db.refresh(design)

            # Unified Response for draft (all fields, null if not present)
            return {
                "status": 1,
                "message": "Draft saved successfully",
                "data": {
                    "exam_name": design.dm_design_name,
                    "exam_code": design.dm_design_code,
                    "status": design.dm_status,
                    "number_of_sets": design.dm_no_of_sets or None,
                    "number_of_versions": design.dm_no_of_versions or None,
                    "no_of_qns": design.dm_total_questions or None,
                    "subject": subject_obj.smt_subject_name,
                    "medium": medium_obj.mmt_medium_name,
                    "exam_type": exam_type_obj.qtm_type_name,
                    "chapter_topics": design.dm_chapter_topics,
                    "questions_to_exclude": design.dm_questions_to_exclude,
                    "shortfall_info": None,
                    "question_papers": None
                }
            }

        # === 2. FINALIZE (status=2) ===
        if payload.status == 2:
            # Mandatory validation for finalized exams
            if not payload.chapters_topics or not isinstance(payload.chapters_topics, list):
                raise HTTPException(status_code=400, detail="chapters_topics are required for finalized exams.")
            if payload.qtn_codes_to_exclude is None:
                payload.qtn_codes_to_exclude = []

            # Directly pass chapters_topics as qns_payload
            selected_codes_result = await select_questions(
                db=db,
                qns_payload=payload.chapters_topics,
                is_ai_selected=payload.is_ai_selected,
                subject_code=payload.subject_code,
                medium_code=payload.medium_code,
                total_questions=payload.no_of_sets * payload.total_questions,  # (Sets x Questions)
                no_of_sets=payload.no_of_sets,
                total_questions_design=payload.total_questions,
                qtn_codes_to_exclude=payload.qtn_codes_to_exclude
            )

            selected_codes = selected_codes_result["selected_question_codes"]

            # Ensure at least total_questions are available to create a valid paper
            if not selected_codes or len(selected_codes) < payload.total_questions:
                raise HTTPException(
                    status_code=400,
                    detail=f"At least {payload.total_questions} questions are required to generate a question paper, "
                        f"but only {len(selected_codes) if selected_codes else 0} were available after filtering."
    )


            # Create finalized design record
            design = await create_design_record(
                db=db,
                payload=payload,
                current_user=current_user,
                design_code=design_code,
                exam_type_obj=exam_type_obj,
                subject_obj=subject_obj,
                medium_obj=medium_obj,
                all_question_codes=selected_codes
            )

            # Save metadata
            design.dm_status = "closed"
            design.dm_chapter_topics = [c.model_dump() for c in payload.chapters_topics]
            design.dm_questions_to_exclude = payload.qtn_codes_to_exclude

            await db.commit()
            await db.refresh(design)

            # Generate versions & sets
            await create_question_paper_details(db, design, selected_codes, payload, current_user)

            # Build final response
            question_papers = await build_response(db, design, include_answers)

            return {
                "status": 2,
                "message": "Exam finalized and question papers generated successfully",
                "data": {
                    "exam_name": design.dm_design_name,
                    "exam_code": design.dm_design_code,
                    "status": design.dm_status,
                    "number_of_sets": design.dm_no_of_sets,
                    "number_of_versions": design.dm_no_of_versions,
                    "no_of_qns": design.dm_total_questions,
                    "subject": subject_obj.smt_subject_name,
                    "medium": medium_obj.mmt_medium_name,
                    "exam_type": exam_type_obj.qtm_type_name,
                    "shortfall_info": selected_codes_result["shortfall"],
                    "question_papers": question_papers
                }
            }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating exam: {str(e)}")

async def update_design_service(
    db: AsyncSession,
    exam_code: str,
    payload: DesignUpdate,
    current_user
):
    # Fetch existing design
    result = await db.execute(select(Design).where(Design.dm_design_code == exam_code))
    design = result.scalar_one_or_none()
    if not design:
        raise HTTPException(status_code=404, detail="Exam design not found")

    # Role validation (admin or owner)
    role_obj = await get_user_role(db, current_user.role_id)
    if not role_obj:
        raise HTTPException(status_code=404, detail="User role not found")
    is_admin = role_obj.role_code == "100"
    if not is_admin and design.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this design")

    # === Duplicate exam name check (only if changed) ===
    if payload.exam_name and payload.exam_name != design.dm_design_name:
        with db.no_autoflush:  # Use synchronous context manager
            await check_existing_design(db, payload.exam_name)

    # Resolve foreign keys (exam type, subject, medium)
    exam_type_obj, subject_obj, medium_obj = await resolve_foreign_keys(db, payload)

    # Update core design fields (map API → DB)
    design.dm_design_name = payload.exam_name or design.dm_design_name
    design.dm_exam_type_id = exam_type_obj.id
    design.dm_subject_id = subject_obj.id
    design.dm_medium_id = medium_obj.id
    design.dm_exam_mode = payload.exam_mode or design.dm_exam_mode
    design.dm_total_time = payload.total_time or design.dm_total_time
    design.dm_total_questions = payload.total_questions or design.dm_total_questions
    design.dm_no_of_versions = payload.no_of_versions or design.dm_no_of_versions
    design.dm_no_of_sets = payload.no_of_sets or design.dm_no_of_sets
    design.dm_standard = payload.standard or design.dm_standard
    design.updated_by = current_user.id
    design.updated_at = datetime.utcnow()

    # === Draft Update (status=1) ===
    if payload.status == 1:
        design.dm_status = "draft"
        design.dm_chapter_topics = (
            [c.model_dump() for c in payload.chapters_topics] if payload.chapters_topics else None
        )
        design.dm_questions_to_exclude = payload.qtn_codes_to_exclude or None

        await db.commit()
        await db.refresh(design)

        return {
            "status": 1,
            "message": "Draft updated successfully",
            "data": {
                "exam_name": design.dm_design_name,
                "exam_code": design.dm_design_code,
                "status": design.dm_status,
                "number_of_sets": design.dm_no_of_sets,
                "number_of_versions": design.dm_no_of_versions,
                "no_of_qns": design.dm_total_questions,
                "subject": subject_obj.smt_subject_name,
                "medium": medium_obj.mmt_medium_name,
                "exam_type": exam_type_obj.qtm_type_name,
                "chapter_topics": design.dm_chapter_topics,
                "questions_to_exclude": design.dm_questions_to_exclude,
            }
        }

    # === Finalize Update (status=2) ===
    if payload.status == 2:
        if not payload.chapters_topics or not isinstance(payload.chapters_topics, list):
            raise HTTPException(status_code=400, detail="chapters_topics required for finalized exams")
        if payload.qtn_codes_to_exclude is None:
            payload.qtn_codes_to_exclude = []

        # Select questions
        selected_codes_result = await select_questions(
            db=db,
            qns_payload=payload.chapters_topics,
            is_ai_selected=payload.is_ai_selected,
            subject_code=payload.subject_code,
            medium_code=payload.medium_code,
            total_questions=payload.no_of_sets * payload.total_questions,
            no_of_sets=payload.no_of_sets,
            total_questions_design=payload.total_questions,
            qtn_codes_to_exclude=payload.qtn_codes_to_exclude
        )
        selected_codes = selected_codes_result["selected_question_codes"]

        if not selected_codes or len(selected_codes) < payload.total_questions:
            raise HTTPException(
                status_code=400,
                detail=f"At least {payload.total_questions} questions are required to generate a question paper, "
                    f"but only {len(selected_codes) if selected_codes else 0} were available after filtering."
    )

        # Update finalized design
        design.dm_status = "closed"
        design.dm_chapter_topics = [c.model_dump() for c in payload.chapters_topics]
        design.dm_questions_to_exclude = payload.qtn_codes_to_exclude
        design.dm_total_question_codes = selected_codes

        await db.commit()
        await db.refresh(design)

        # Generate question papers
        await create_question_paper_details(db, design, selected_codes, payload, current_user)

        include_answers = role_obj.role_code == "100"
        question_papers = await build_response(db, design, include_answers)

        return {
            "status": 2,
            "message": "Exam finalized and question papers generated successfully",
            "data": {
                "exam_name": design.dm_design_name,
                "exam_code": design.dm_design_code,
                "status": design.dm_status,
                "number_of_sets": design.dm_no_of_sets,
                "number_of_versions": design.dm_no_of_versions,
                "no_of_qns": design.dm_total_questions,
                "subject": subject_obj.smt_subject_name,
                "medium": medium_obj.mmt_medium_name,
                "exam_type": exam_type_obj.qtm_type_name,
                "shortfall_info": selected_codes_result["shortfall"],
                "question_papers": question_papers,
            }
        }