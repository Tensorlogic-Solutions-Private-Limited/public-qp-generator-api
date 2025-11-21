from sqlalchemy import select
from app.models.master import Medium, Subject, Question_Format as Format, Question_Type
# from app.schemas.pydantic_models import MediumBase, MediumResponse, SubjectBase, SubjectListResponse, FormatBase, FormatResponse, QuestionTypeBase, QuestionTypeListResponse
from app.schemas.metadata import MediumBase, MediumResponse, SubjectBase, SubjectListResponse, FormatBase, FormatResponse, QuestionTypeBase, QuestionTypeListResponse

from sqlalchemy.orm import selectinload

# === Get All Mediums ===
async def get_all_mediums(db):
    result = await db.execute(select(Medium))
    mediums = result.scalars().all()
    data = [
        MediumBase(
            medium_code=m.mmt_medium_code,
            medium_name=m.mmt_medium_name
        ) for m in mediums
    ]
    return MediumResponse(data=data)


# === Get All Subjects ===
async def get_all_subjects(db):
    result = await db.execute(
        select(Subject).options(selectinload(Subject.medium))
    )
    subjects = result.scalars().all()

    data = [
        SubjectBase(
            subject_code=s.smt_subject_code,
            subject_name=s.smt_subject_name,
            medium_code=s.medium.mmt_medium_code if s.medium else None,
            standard=s.smt_standard
        ) for s in subjects
    ]
    return SubjectListResponse(data=data)


# === Get All Formats ===
async def get_all_formats(db):
    result = await db.execute(select(Format))
    formats = result.scalars().all()
    data = [
        FormatBase(
            qfm_format_code=f.qfm_format_code,
            qfm_format_name=f.qfm_format_name
        ) for f in formats
    ]
    return FormatResponse(data=data)


# === Get All Question Types ===
async def get_all_question_types(db):
    result = await db.execute(select(Question_Type))
    types = result.scalars().all()
    data = [
        QuestionTypeBase(
            type_code=t.qtm_type_code,
            type_name=t.qtm_type_name
        ) for t in types
    ]
    return QuestionTypeListResponse(data=data)

