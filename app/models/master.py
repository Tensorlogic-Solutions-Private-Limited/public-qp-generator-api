from sqlalchemy import Column, Integer, String, Boolean, ForeignKey,Text, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.audit_mixin import AuditMixin
from sqlalchemy import JSON

class Question_Type(Base, AuditMixin):
    __tablename__ = "question_type_master"

    id = Column(Integer, primary_key=True, index=True)
    qtm_type_code = Column(String, unique=True, nullable=False)
    qtm_type_name = Column(String, unique=True, nullable=False)

    questions = relationship("Questions", back_populates="type")
    designs = relationship("Design", back_populates="type")


class Question_Format(Base, AuditMixin):
    __tablename__ = "question_format_master"

    id = Column(Integer, primary_key=True, index=True)
    qfm_format_code = Column(String, unique=True, nullable=False)
    qfm_format_name = Column(String, unique=True, nullable=False)

    questions = relationship("Questions", back_populates="format")


class Medium(Base, AuditMixin):
    __tablename__ = "medium_master_table"

    id = Column(Integer, primary_key=True, index=True)
    mmt_medium_code = Column(String, unique=True, nullable=False)
    mmt_medium_name = Column(String, unique=True, nullable=False)

    # Relationships
    subjects = relationship("Subject", back_populates="medium", cascade="all, delete")
    designs = relationship("Design", back_populates="medium", cascade="all, delete")
    taxonomies = relationship("Taxonomy", back_populates="medium", cascade="all, delete-orphan")


class Criteria(Base, AuditMixin):
    __tablename__ = "selection_criteria_master"

    id = Column(Integer, primary_key=True, index=True)
    scm_criteria_code = Column(String, unique=True, nullable=False)
    scm_criteria_name = Column(String, unique=True, nullable=False)


class Subject(Base, AuditMixin):
    __tablename__ = "subject_master_table"

    id = Column(Integer, primary_key=True, index=True)
    smt_subject_code = Column(String, unique=True, nullable=False)
    smt_subject_name = Column(String, unique=True, nullable=False)
    smt_standard = Column(String, nullable=False)

    smt_medium_id = Column(Integer, ForeignKey("medium_master_table.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    medium = relationship("Medium", back_populates="subjects", cascade="all, delete")
    designs = relationship("Design", back_populates="subject", cascade="all, delete-orphan")
    taxonomies = relationship("Taxonomy", back_populates="subject", cascade="all, delete-orphan")


class Taxonomy(Base, AuditMixin):
    __tablename__ = "subject_taxonomy_master"

    id = Column(Integer, primary_key=True, index=True)
    stm_taxonomy_code = Column(String, unique=True, nullable=False)
    stm_subject_id = Column(Integer, ForeignKey("subject_master_table.id", ondelete="CASCADE"), nullable=False)
    stm_medium_id = Column(Integer, ForeignKey("medium_master_table.id", ondelete="CASCADE"), nullable=False)
    stm_standard = Column(String, nullable=False)
    stm_chapter_code = Column(String, nullable=False)
    stm_chapter_name = Column(String, nullable=False)
    stm_topic_code = Column(String, unique=True, nullable=False)
    stm_topic_name = Column(String, unique=True, nullable=False)

    # Relationships
    questions = relationship("Questions", back_populates="taxonomy")
    subject = relationship("Subject", back_populates="taxonomies")
    medium = relationship("Medium", back_populates="taxonomies")


class Questions(Base, AuditMixin):
    __tablename__ = "question_master_table"

    id = Column(Integer, primary_key=True, index=True)
    qmt_question_code = Column(String, unique=True, nullable=False)
    qmt_question_text = Column(Text, nullable=False)
    qmt_option1 = Column(String, nullable=False)
    qmt_option2 = Column(String, nullable=False)
    qmt_option3 = Column(String, nullable=False)
    qmt_option4 = Column(String, nullable=False)
    qmt_correct_answer = Column(String, nullable=False)
    qmt_marks = Column(Integer, nullable=False)
    qmt_format_id = Column(Integer, ForeignKey("question_format_master.id", ondelete="CASCADE"), nullable=False)
    qmt_type_id = Column(Integer, ForeignKey("question_type_master.id", ondelete="CASCADE"), nullable=False)
    qmt_taxonomy_id = Column(Integer, ForeignKey("subject_taxonomy_master.id", ondelete="CASCADE"), nullable=False)
    qmt_taxonomy_code = Column(String, nullable=False)
    qmt_is_active = Column(Boolean, default=True)

    # Relationships
    format = relationship("Question_Format", back_populates="questions")
    type = relationship("Question_Type", back_populates="questions")
    taxonomy = relationship("Taxonomy", back_populates="questions")




# class Design(Base, AuditMixin):
#     __tablename__ = "design_master"

#     id = Column(Integer, primary_key=True, index=True)
#     dm_design_name = Column(String, unique=True, nullable=False)
#     dm_design_code = Column(String, unique=True, nullable=False)
#     dm_exam_type_id = Column(Integer, ForeignKey("question_type_master.id", ondelete="CASCADE"), nullable=False)
#     dm_exam_mode = Column(String, nullable=False)

#     dm_total_time = Column(Integer, nullable=False, comment="Total duration of the exam in minutes")
#     dm_total_questions = Column(Integer, nullable=False, comment="Total number of questions")
#     dm_no_of_versions = Column(Integer, nullable=False, comment="Number of versions")
#     dm_no_of_sets = Column(Integer, nullable=False, comment="Number of sets")

#     dm_subject_id = Column(Integer, ForeignKey("subject_master_table.id", ondelete="CASCADE"), nullable=False)
#     dm_medium_id = Column(Integer, ForeignKey("medium_master_table.id", ondelete="CASCADE"), nullable=False)
#     dm_standard = Column(String, nullable=False)
#     dm_status = Column(Enum("draft", "closed", name="dm_status_enum"), nullable=False, server_default="draft")
#     dm_total_question_codes = Column(JSON, nullable=False)

#     dm_chapter_topics = Column(JSON, nullable=True)
#     dm_questions_to_exclude = Column(JSON, nullable=True)

#     # Relationships
#     subject = relationship("Subject", back_populates="designs")
#     medium = relationship("Medium", back_populates="designs")
#     type = relationship("Question_Type", back_populates="designs")
#     question_papers = relationship("QuestionPaperDetails", back_populates="design", cascade="all, delete-orphan")

class Design(Base, AuditMixin):
    __tablename__ = "design_master"

    id = Column(Integer, primary_key=True, index=True)
    dm_design_name = Column(String, unique=True, nullable=False)
    dm_design_code = Column(String, unique=True, nullable=False)
    dm_exam_type_id = Column(Integer, ForeignKey("question_type_master.id", ondelete="CASCADE"), nullable=True)  # Draft-friendly
    dm_exam_mode = Column(String, nullable=True)  #  Draft-friendly

    dm_total_time = Column(Integer, nullable=True, comment="Total duration of the exam in minutes")  # Draft-friendly
    dm_total_questions = Column(Integer, nullable=True, comment="Total number of questions")  # Draft-friendly
    dm_no_of_versions = Column(Integer, nullable=True, comment="Number of versions")  # Draft-friendly
    dm_no_of_sets = Column(Integer, nullable=True, comment="Number of sets")  # Draft-friendly

    dm_subject_id = Column(Integer, ForeignKey("subject_master_table.id", ondelete="CASCADE"), nullable=True)  # Draft-friendly
    dm_medium_id = Column(Integer, ForeignKey("medium_master_table.id", ondelete="CASCADE"), nullable=True)  # Draft-friendly
    dm_standard = Column(String, nullable=True)  # Draft-friendly
    
    dm_status = Column(Enum("draft", "closed", name="dm_status_enum"), nullable=False, server_default="draft")
    dm_total_question_codes = Column(JSON, nullable=True)  # Draft: No questions yet

    dm_chapter_topics = Column(JSON, nullable=True)
    dm_questions_to_exclude = Column(JSON, nullable=True)

    # Relationships
    subject = relationship("Subject", back_populates="designs")
    medium = relationship("Medium", back_populates="designs")
    type = relationship("Question_Type", back_populates="designs")
    question_papers = relationship("QuestionPaperDetails", back_populates="design", cascade="all, delete-orphan")


class QuestionPaperDetails(Base, AuditMixin):
    __tablename__ = "question_paper_details"

    id = Column(Integer, primary_key=True, index=True) # primary key
    qpd_paper_id = Column(Text, nullable=False) # paper code for each questionpaper
    qpd_q_codes = Column(JSON, nullable=False) #question codes of each questionpaper
    qpd_total_time = Column(Integer,nullable=False)
    qpd_total_questions = Column(Integer,nullable=False)# total no of questions for each qustion paper
    qpd_design_name = Column(Text,nullable=False) #design name form Design table
    qpd_design_id = Column(Integer, ForeignKey("design_master.id", ondelete="CASCADE"), nullable=False)# primary key from the design table

    # Relationships
    design = relationship("Design", back_populates="question_papers")






    



    

