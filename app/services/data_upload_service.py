import pandas as pd
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import Role
from app.models.master import Question_Type, Medium, Subject, Criteria, Question_Format, Taxonomy, Questions
from app.database import Base, engine
from fastapi import HTTPException, status
from io import BytesIO
from fastapi.responses import StreamingResponse
from openpyxl import Workbook

async def load_excel(file_path: str) -> pd.DataFrame:
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File not found at {file_path}")

    try:
        df = pd.read_excel(file_path)
        if df.empty:
            raise HTTPException(status_code=400, detail="Excel file is empty")
        return df
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading Excel: {str(e)}")

async def insert_if_missing(db: AsyncSession, model, defaults):
    result = await db.execute(select(model))
    existing = result.scalars().first()
    if not existing:
        db.add_all(defaults)

async def upload_excel_to_db(db: AsyncSession, file_path: str):
    # Create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Insert master data if missing
    await insert_if_missing(db, Role, [
        Role(role_name="admin", role_code="100"),
        Role(role_name="educator", role_code="101")
    ])
    await insert_if_missing(db, Question_Type, [Question_Type(qtm_type_code="1000", qtm_type_name="MCQ")])
    await insert_if_missing(db, Medium, [Medium(mmt_medium_code="2000", mmt_medium_name="English")])
    await insert_if_missing(db, Subject, [
        Subject(smt_subject_code="3000", smt_subject_name="Social Science", smt_standard="10", smt_medium_id=1)
    ])
    await insert_if_missing(db, Criteria, [
        Criteria(scm_criteria_code="4000", scm_criteria_name="Chapter"),
        Criteria(scm_criteria_code="4001", scm_criteria_name="Topic")
    ])
    await insert_if_missing(db, Question_Format, [Question_Format(qfm_format_code="5000", qfm_format_name="Text")])
    await db.commit()

    # Load Excel Data
    df = await load_excel(file_path)

    taxonomy_mappings = {}

    # Insert taxonomy data
    for _, row in df.iterrows():
        result = await db.execute(
            select(Taxonomy).where(Taxonomy.stm_topic_name == row['topic_name'])
        )
        existing = result.scalars().first()
        key = (str(row['chapter_code']), str(row['topic_code']))

        if existing:
            taxonomy_mappings[key] = (existing.id, existing.stm_taxonomy_code)
            continue

        taxonomy = Taxonomy(
            stm_taxonomy_code=f"TAX{str(row['chapter_code'])}{str(row['topic_code'])}",
            stm_subject_id=row['subject_id'],
            stm_medium_id=row['medium_id'],
            stm_chapter_code=str(row['chapter_code']),
            stm_chapter_name=row['chapter_name'],
            stm_topic_code=str(row['topic_code']),
            stm_topic_name=row['topic_name'],
            stm_standard=str(row['standard'])
        )
        db.add(taxonomy)
        await db.flush()
        await db.refresh(taxonomy)
        taxonomy_mappings[key] = (taxonomy.id, taxonomy.stm_taxonomy_code)

    await db.commit()

    # Insert questions
    for _, row in df.iterrows():
        taxonomy_id, taxonomy_code = taxonomy_mappings.get(
            (str(row['chapter_code']), str(row['topic_code'])), (None, None)
        )
        if taxonomy_id is None:
            continue

        result = await db.execute(
            select(Questions).where(Questions.qmt_question_code == f"Q{row['q_id']}")
        )
        existing_question = result.scalars().first()
        if not existing_question:
            question = Questions(
                qmt_question_code=f"Q{row['q_id']}",
                qmt_question_text=str(row['q_text']),
                qmt_option1=str(row['qat_option1']),
                qmt_option2=str(row['qat_option2']),
                qmt_option3=str(row['qat_option3']),
                qmt_option4=str(row['qat_option4']),
                qmt_correct_answer=str(row['qat_correct_answer']),
                qmt_marks=1,
                qmt_format_id=1,
                qmt_type_id=1,
                qmt_taxonomy_id=taxonomy_id,
                qmt_taxonomy_code=taxonomy_code,
                qmt_is_active=True
            )
            db.add(question)

    await db.commit()
    return {"message": "Excel data uploaded successfully"}

def generate_excel_template():
    wb = Workbook()

    # Sheet 1: Template
    ws_template = wb.active
    ws_template.title = "Questions"
    ws_template.append([
        "q_id", "q_text", "chapter_name", "topic_name",
        "class_studying_id", "subject_id", "subject_name",
        "subject_code", "medium_code",
        "qat_option1", "qat_option2", "qat_option3", "qat_option4",
        "qat_correct_answer"
    ])
    ws_template.append([
        1, "What is the capital of India?", "Geography", "Capital Cities",
        "10", 1, "Social Science", "3000", "2000",
        "Delhi", "Mumbai", "Chennai", "Kolkata", "qat_option1"
    ])

    # Sheet 2: Instructions
    ws_instructions = wb.create_sheet(title="Instructions")
    instructions = [
        "To ensure a successful data upload, each row must follow the structure below. "
        "Fill in the required details for each column as per the given instructions:",

        "1. 'q_id': Provide a unique number for each question.",
        "2. 'q_text': Enter the full text of the question.",
        "3. 'chapter_name': Specify the chapter to which the question belongs.",
        "4. 'topic_name': Mention the specific topic under the chapter.",
        "5. 'class_studying_id': Indicate the class/grade level for the question.",
        "6. 'subject_id': Provide the subject’s unique identifier.",
        "7. 'subject_name': Enter the name of the subject.",
        "8. 'subject_code': Use the official subject code for reference.",
        "9. 'medium_code': Specify the language/medium of instruction.",
        "10. 'qat_option1': Enter the first answer option.",
        "11. 'qat_option2': Enter the second answer option.",
        "12. 'qat_option3': Enter the third answer option.",
        "13. 'qat_option4': Enter the fourth answer option.",
        "14. 'qat_correct_answer': Specify the correct option (e.g., 'qat_option1', 'qat_option2', etc.). "
        "Ensure this value matches one of the provided answer choices.",
        "15. Review the data for accuracy and completeness before submission."
    ]

    for row in instructions:
        ws_instructions.append([row])

    # Return Excel file as response
    stream = BytesIO()
    wb.save(stream)
    stream.seek(0)

    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=Question_Answer_Template.xlsx"}
    )