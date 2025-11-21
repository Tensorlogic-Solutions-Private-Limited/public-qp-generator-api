import asyncio
from sqlalchemy.future import select
from app.database import AsyncSessionLocal, Base, engine
from app.models.user import Role, User
from app.models.master import *
from app.utils.auth import get_password_hash

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # Insert Roles if missing
        result = await session.execute(select(Role))
        if not result.scalar():
            session.add_all([
                Role(role_name="admin", role_code="100"),
                Role(role_name="educator", role_code="101")
            ])
            await session.commit()

        # Insert Question_Type
        result = await session.execute(select(Question_Type))
        if not result.scalar():
            session.add_all([
                Question_Type(qtm_type_code="1000", qtm_type_name="MCQ")
            ])
            await session.commit()

        # Insert Medium
        result = await session.execute(select(Medium))
        if not result.scalar():
            session.add_all([
                Medium(mmt_medium_code="2000", mmt_medium_name="English")
            ])
            await session.commit()

        # Insert Subject
        result = await session.execute(select(Subject))
        if not result.scalar():
            session.add_all([
                Subject(
                    smt_subject_code="3000",
                    smt_subject_name="Social Science",
                    smt_standard="10",
                    smt_medium_id=1  # Ensure this Medium ID exists
                )
            ])
            await session.commit()

        # Insert Criteria
        result = await session.execute(select(Criteria))
        if not result.scalar():
            session.add_all([
                Criteria(scm_criteria_code="4000", scm_criteria_name="Chapter"),
                Criteria(scm_criteria_code="4001", scm_criteria_name="Topic")
            ])
            await session.commit()

        # Insert Question_Format
        result = await session.execute(select(Question_Format))
        if not result.scalar():
            session.add_all([
                Question_Format(qfm_format_code="5000", qfm_format_name="Text")
            ])
            await session.commit()

        # 🔐 Create 'superadmin' user with admin role if not exists
        result = await session.execute(select(User).where(User.username == "admin"))
        existing_user = result.scalar_one_or_none()
        if not existing_user:
            role_result = await session.execute(select(Role).where(Role.role_code == "100"))
            admin_role = role_result.scalar_one()

            new_user = User(
                username="admin",
                hashed_password=get_password_hash("admin"),
                role_id=admin_role.id,
                is_active=True
            )
            session.add(new_user)
            await session.commit()
            print("admin user created with admin role.")

if __name__ == "__main__":
    asyncio.run(init_db())