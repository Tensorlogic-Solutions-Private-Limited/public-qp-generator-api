from pydantic import BaseModel, ConfigDict,Field, root_validator
from typing import Optional, List, Literal
from datetime import datetime
from pydantic import BaseModel
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from enum import Enum
from pydantic import BaseModel, root_validator, validator
from pydantic import BaseModel, field_validator, model_validator
from typing import List, Optional, Union

############# Design Create #############
from pydantic import BaseModel, model_validator
from typing import List, Optional, Literal

class CodeSelection(BaseModel):
    code: str
    qn_count: Optional[int] = None

class QuestionSelection(BaseModel):
    type: str
    codes: List[CodeSelection]

from app.constants.status_codes import DESIGN_STATUS

class DesignBase(BaseModel):
    status: int
    is_ai_selected: bool
    exam_name: str
    exam_type_code: Optional[str] = None
    subject_code: Optional[str] = None
    medium_code: Optional[str] = None
    exam_mode: Optional[str] = None
    total_time: Optional[int] = None
    total_questions: Optional[int] = None
    no_of_versions: Optional[int] = None
    no_of_sets: Optional[int] = None
    standard: Optional[str] = None
    qtn_codes_to_exclude: List[str] = []
    chapters_topics: List[QuestionSelection] = []

    @model_validator(mode="after")
    def validate_based_on_status(self):
        status_label = DESIGN_STATUS.get(self.status)

        if status_label == "closed":
            # Validate required fields for finalization
            required_fields = [
                "exam_type_code", "subject_code", "medium_code", "exam_mode",
                "total_time", "total_questions", "no_of_versions", "no_of_sets"
            ]
            for field in required_fields:
                if getattr(self, field) is None:
                    raise ValueError(f"{field} is required when status is 'closed'")

            # Validate question count rules
            if self.is_ai_selected:
                for q in self.chapters_topics:
                    for code in q.codes:
                        if code.qn_count is not None:
                            raise ValueError("When 'is_ai_selected' is True, 'qn_count' must be null or omitted.")
            else:
                for q in self.chapters_topics:
                    for code in q.codes:
                        if code.qn_count is None:
                            raise ValueError("When 'is_ai_selected' is False, each 'qn_count' must be provided.")

        return self

class DesignCreate(BaseModel):
    is_ai_selected: bool
    exam_name: str
    exam_type_code: str
    subject_code: str
    medium_code: str
    exam_mode: str
    total_time: int
    total_questions: int
    no_of_versions: int
    no_of_sets: int
    standard: Optional[str]
    qtn_codes_to_exclude: List[str] = []
    chapters_topics: List[QuestionSelection]

    @model_validator(mode="after")
    def validate_qn_count(self) -> 'DesignCreate':
        if self.is_ai_selected:
            for q in self.chapters_topics:
                for code in q.codes:
                    if code.qn_count is not None:
                        raise ValueError("When 'is_ai_selected' is True, 'qn_count' must be null or omitted.")
        else:
            for q in self.chapters_topics:
                for code in q.codes:
                    if code.qn_count is None:
                        raise ValueError("When 'is_ai_selected' is False, each 'qn_count' must be provided.")
        return self


class DesignPaperListResponseItem(BaseModel):
    exam_name: str
    exam_code: str
    exam_type: Optional[str] = None
    exam_mode: Optional[str] = None   # ✅ was str
    standard: Optional[str] = None
    subject: Optional[str] = None
    medium: Optional[str] = None
    status: str
    number_of_sets: Optional[int] = None   # ✅ was int
    number_of_versions: Optional[int] = None  # ✅ was int
    total_questions: Optional[int] = None  # ✅ was int
    created_at: str
    created_by: Optional[str] = None
    created_by_id: int

class DesignUpdate(BaseModel):
    exam_name: Optional[str]
    exam_type_code: Optional[str]
    exam_mode: Optional[str]
    total_time: Optional[int]
    total_questions: Optional[int]
    no_of_versions: Optional[int]
    no_of_sets: Optional[int]
    subject_code: Optional[str]
    medium_code: Optional[str]
    standard: Optional[str]
    is_ai_selected: Optional[bool] = False
    qtn_codes_to_exclude: Optional[List[str]] = []
    chapters_topics: Optional[List[QuestionSelection]] = None
    status: Optional[int]  # 1=draft, 2=finalized

class DesignPaperResponse(BaseModel):
    exam_name: str
    exam_code: str
    exam_type: Optional[str] = None
    exam_mode: Optional[str] = None
    standard: Optional[str] = None
    subject: Optional[str] = None
    medium: Optional[str] = None
    status: str
    number_of_sets: Optional[int] = None
    number_of_versions: Optional[int] = None
    total_questions: Optional[int] = None
    papers: List[str] = []

class SingleDesignResponse(BaseModel):
    design: DesignPaperResponse

class DesignPaperListResponse(BaseModel):
    exams: List[DesignPaperListResponseItem]

