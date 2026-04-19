from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.core.db import Base
import datetime

class PatientReport(Base):
    """
    SQLAlchemy model for storing parsed reports and their analysis.
    Stores the raw JSON structures as Text so we can deserialize them easily.
    """
    __tablename__ = "patient_reports"

    id = Column(Integer, primary_key=True, index=True)
    patient_name = Column(String(255), index=True)
    report_date = Column(String(50))
    created_at = Column(DateTime, default=datetime.datetime.utcnow, server_default=func.now())
    
    # Store complete LabReport JSON
    lab_report_data = Column(Text, nullable=False)
    
    # Store complete SummaryAnalysis JSON
    analysis_data = Column(Text, nullable=False)
