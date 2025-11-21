import pandas as pd
import os
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import AsyncSessionLocal, Base, engine  # include engine here
from app.models.user import Role
from app.models.master import Question_Type, Medium, Subject, Criteria, Question_Format, Taxonomy, Questions

async def load_data():
    file_path = "Updated_Question_Answer_Modified.xlsx"
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return pd.DataFrame()

    try:
        df = pd.read_excel(file_path)
        print(f"Excel loaded: {len(df)} rows.")
        return df
    except Exception as e:
        print(f"Error loading Excel: {e}")
        return pd.DataFrame()

async def init_db():
    try:
        print("Creating tables if not exist...")

        # ✅ Use engine.begin() to call run_sync for create_all
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with AsyncSessionLocal() as db:
            async with db.begin():
                async def insert_if_missing(model, defaults):
                    result = await db.execute(select(model))
                    existing = result.scalars().first()
                    if not existing:
                        db.add_all(defaults)
                        print(f"Inserted defaults for {model.__name__}")

                await insert_if_missing(Role, [
                    Role(role_name="admin", role_code="100"),
                    Role(role_name="teacher", role_code="101")
                ])
                await insert_if_missing(Question_Type, [Question_Type(qtm_type_code="1000", qtm_type_name="MCQ")])
                await insert_if_missing(Medium, [Medium(mmt_medium_code="2000", mmt_medium_name="English")])
                await insert_if_missing(Subject, [
                    Subject(smt_subject_code="3000", smt_subject_name="Social Science", smt_standard="10", smt_medium_id=1)
                ])
                await insert_if_missing(Criteria, [
                    Criteria(scm_criteria_code="4000", scm_criteria_name="Chapter"),
                    Criteria(scm_criteria_code="4001", scm_criteria_name="Topic")
                ])
                await insert_if_missing(Question_Format, [Question_Format(qfm_format_code="5000", qfm_format_name="Text")])

                await db.commit()

            # Load Excel data
            df = await load_data()
            if df.empty:
                print("No data to process.")
                return

            taxonomy_mappings = {}

            for _, row in df.iterrows():
                result = await db.execute(
                    select(Taxonomy).where(Taxonomy.stm_topic_name == row['topic_name'])
                )
                existing = result.scalars().first()
                key = (str(row['chapter_code']), str(row['topic_code']))  # Cast to str here

                if existing:
                    taxonomy_mappings[key] = (existing.id, existing.stm_taxonomy_code)
                    continue

                taxonomy = Taxonomy(
                    stm_taxonomy_code=f"TAX{str(row['chapter_code'])}{str(row['topic_code'])}",  # Cast to str
                    stm_subject_id=row['subject_id'],
                    stm_medium_id=row['medium_id'],
                    stm_chapter_code=str(row['chapter_code']),     # ✅ must be str
                    stm_chapter_name=row['chapter_name'],
                    stm_topic_code=str(row['topic_code']),         # ✅ must be str
                    stm_topic_name=row['topic_name'],
                    stm_standard=str(row['standard'])
                )
                db.add(taxonomy)
                await db.flush()
                await db.refresh(taxonomy)
                taxonomy_mappings[key] = (taxonomy.id, taxonomy.stm_taxonomy_code)

            await db.commit()

            # Add questions
            for _, row in df.iterrows():
                taxonomy_id, taxonomy_code = taxonomy_mappings.get(
                    (str(row['chapter_code']), str(row['topic_code'])), (None, None)  # Cast to str here
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
            print("✔ All done.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(init_db())
