from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from collections import defaultdict
from fastapi import HTTPException, status
from app.models.master import Taxonomy, Subject, Medium, Questions, Question_Type
from app.schemas.questions import ChapterCountResponse, ExamQuestionsResponse, ExamQuestionResponse, ExamQuestionGroupResponse

async def get_chapter_topic_question_counts(standard: str, medium_code: str, subject_code: str, db):
    chapter_stmt = (
        select(
            Taxonomy.stm_chapter_code.label("chapter_code"),
            Taxonomy.stm_chapter_name.label("chapter_name"),
            func.count(Questions.id).label("chapter_question_count")
        )
        .join(Questions, Questions.qmt_taxonomy_id == Taxonomy.id)
        .join(Subject, Taxonomy.stm_subject_id == Subject.id)
        .join(Medium, Taxonomy.stm_medium_id == Medium.id)
        .where(
            Taxonomy.stm_standard == standard,
            Subject.smt_subject_code == subject_code,
            Medium.mmt_medium_code == medium_code,
        )
        .group_by(Taxonomy.stm_chapter_code, Taxonomy.stm_chapter_name)
        .order_by(Taxonomy.stm_chapter_code)
    )
    chapter_result = await db.execute(chapter_stmt)
    chapter_rows = chapter_result.all()

    topic_stmt = (
        select(
            Taxonomy.stm_chapter_code.label("chapter_code"),
            Taxonomy.stm_topic_code.label("topic_code"),
            Taxonomy.stm_topic_name.label("topic_name"),
            func.count(Questions.id).label("topic_question_count")
        )
        .join(Questions, Questions.qmt_taxonomy_id == Taxonomy.id)
        .join(Subject, Taxonomy.stm_subject_id == Subject.id)
        .join(Medium, Taxonomy.stm_medium_id == Medium.id)
        .where(
            Taxonomy.stm_standard == standard,
            Subject.smt_subject_code == subject_code,
            Medium.mmt_medium_code == medium_code,
        )
        .group_by(
            Taxonomy.stm_chapter_code,
            Taxonomy.stm_topic_code,
            Taxonomy.stm_topic_name
        )
        .order_by(
            Taxonomy.stm_chapter_code,
            Taxonomy.stm_topic_code
        )
    )
    topic_result = await db.execute(topic_stmt)
    topic_rows = topic_result.all()

    chapter_to_topics = defaultdict(list)
    for topic in topic_rows:
        chapter_to_topics[topic.chapter_code].append({
            "code": topic.topic_code,
            "name": topic.topic_name,
            "question_count": topic.topic_question_count,
            "subtopics": []
        })

    final_chapters = []
    for chapter in chapter_rows:
        final_chapters.append({
            "code": chapter.chapter_code,
            "name": chapter.chapter_name,
            "question_count": chapter.chapter_question_count,
            "topics": chapter_to_topics.get(chapter.chapter_code, [])
        })

    # return ChapterCountResponse(chapters=final_chapters)
    return ChapterCountResponse(data=final_chapters)


async def get_questions_by_filters(filter_type: str, codes: str, db):
    if filter_type not in ["chapter", "topic"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid type. Must be 'chapter' or 'topic'.")

    code_list = [c.strip() for c in codes.split(",") if c.strip()]
    if not code_list:
        return ExamQuestionsResponse(qn_groups=[], qns=[])

    filter_column = Taxonomy.stm_chapter_code if filter_type == "chapter" else Taxonomy.stm_topic_code

    stmt = (
        select(Questions)
        .join(Taxonomy, Questions.qmt_taxonomy_id == Taxonomy.id)
        .join(Question_Type, Questions.qmt_type_id == Question_Type.id)
        .where(filter_column.in_(code_list))
        .options(joinedload(Questions.taxonomy), joinedload(Questions.type))
    )
    result = await db.execute(stmt)
    questions = result.scalars().all()

    qns_list = []
    type_codes_set = set()
    type_names_set = set()

    for q in questions:
        taxonomy = q.taxonomy
        grp_code = taxonomy.stm_chapter_code if filter_type == "chapter" else taxonomy.stm_topic_code
        grp_name = taxonomy.stm_chapter_name if filter_type == "chapter" else taxonomy.stm_topic_name
        type_codes_set.add(grp_code)
        type_names_set.add(grp_name)

        qns_list.append(ExamQuestionResponse(
            code=q.qmt_question_code,
            type=q.type.qtm_type_name,
            marks=q.qmt_marks,
            difficulty_level="Medium",
            grp_type=filter_type,
            grp_type_name=grp_name,
            grp_type_code=grp_code,
            text=q.qmt_question_text
        ))

    qn_groups = [ExamQuestionGroupResponse(
        type=filter_type,
        type_codes=list(type_codes_set),
        type_names=list(type_names_set),
        no_of_qns=len(qns_list)
    )]

    return ExamQuestionsResponse(
        qn_groups=qn_groups,
        qns=qns_list
    )
