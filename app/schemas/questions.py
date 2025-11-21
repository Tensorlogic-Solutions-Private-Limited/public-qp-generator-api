from pydantic import BaseModel, ConfigDict,Field
from typing import Optional, List, Literal
from datetime import datetime
from pydantic import BaseModel
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from enum import Enum
from pydantic import BaseModel, root_validator, validator
from pydantic import BaseModel, field_validator, model_validator
from typing import Optional

############## questions/quesiton_service ################
class SubtopicQuestionCount(BaseModel):
    code: str = Field(..., description="Subtopic code")
    name: str = Field(..., description="Subtopic name")
    question_count: int = Field(..., description="Number of questions under the subtopic")

class TopicQuestionCount(BaseModel):
    code: str = Field(..., description="Topic code")
    name: str = Field(..., description="Topic name")
    question_count: int = Field(..., description="Number of questions under the topic")
    subtopics: List[SubtopicQuestionCount] = Field(default_factory=list, description="List of subtopics")

class ChapterQuestionCount(BaseModel):
    code: str = Field(..., description="Chapter code")
    name: str = Field(..., description="Chapter name")
    question_count: int = Field(..., description="Number of questions under the chapter")
    topics: List[TopicQuestionCount] = Field(default_factory=list, description="List of topics under the chapter")

class ChapterCountResponse(BaseModel):
    data: List[ChapterQuestionCount] = Field(..., description="List of chapters with topic and question count")

class ChapterTopicQuestionCountResponse(ChapterCountResponse):
    pass  # Alias for clarity and flexibility in routing

###get questions #############
class ExamQuestionGroupResponse(BaseModel):
    type: str
    type_codes: List[str]
    type_names: List[str]
    no_of_qns: int

class ExamQuestionResponse(BaseModel):
    code: str
    type: str
    marks: int
    difficulty_level: str
    grp_type: str
    grp_type_name: str
    grp_type_code: str
    text: str

class ExamQuestionsResponse(BaseModel):
    qn_groups: List[ExamQuestionGroupResponse]
    qns: List[ExamQuestionResponse]