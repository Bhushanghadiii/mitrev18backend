from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.database import engine, Base
from app.api.v1 import auth, assessments, questionnaire, gap_analysis, reports

settings = get_settings()
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="MITRE ATT&CK v18 SaaS Gap Analysis"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["Auth"])
app.include_router(assessments.router, prefix=f"{settings.API_V1_PREFIX}/assessments", tags=["Assessments"])
app.include_router(questionnaire.router, prefix=f"{settings.API_V1_PREFIX}/questionnaire", tags=["Questionnaire"])
app.include_router(gap_analysis.router, prefix=f"{settings.API_V1_PREFIX}/gap-analysis", tags=["Gap Analysis"])
app.include_router(reports.router, prefix=f"{settings.API_V1_PREFIX}/reports", tags=["Reports"])

@app.get("/")
async def root():
    return {"message": settings.APP_NAME, "version": settings.VERSION}

@app.get("/health")
async def health():
    return {"status": "healthy"}
    