from fastapi import APIRouter

from .metadata import router as dropdowns_router
from .questions import router as questions_router
from .exams import router as exams_router
from .qn_papers import router as papers_router
from .qn_paper_views import router as papers_view_router
from .file_upload import router as file_upload_router

api_router = APIRouter()

api_router.include_router(dropdowns_router)
api_router.include_router(questions_router)
api_router.include_router(exams_router)
api_router.include_router(papers_router)
api_router.include_router(papers_view_router)
api_router.include_router(file_upload_router)
