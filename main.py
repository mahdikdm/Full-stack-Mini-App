from typing import Optional, List
from sqlmodel import SQLModel, Field, Session, create_engine, select
from fastapi import FastAPI, HTTPException
import uvicorn

DATABASE_URL = "sqlite:///students.db"
engine = create_engine(DATABASE_URL, echo=False)

class Student(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    first_name: str
    last_name: str
    email: str
    major: Optional[str] = None
    gpa: Optional[float] = Field(default=None, ge=0.0, le=4.0)

def init_db():
    SQLModel.metadata.create_all(engine)

app = FastAPI(title="Student Management API", version="0.1.0")

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/students", response_model=List[Student])
def list_students():
    with Session(engine) as session:
        return session.exec(select(Student)).all()

@app.post("/students", response_model=Student, status_code=201)
def create_student(student: Student):
    with Session(engine) as session:
        session.add(student)
        session.commit()
        session.refresh(student)
        return student

@app.get("/students/{student_id}", response_model=Student)
def get_student(student_id: int):
    with Session(engine) as session:
        s = session.get(Student, student_id)
        if not s:
            raise HTTPException(status_code=404, detail="Student not found")
        return s

@app.put("/students/{student_id}", response_model=Student)
def update_student(student_id: int, data: Student):
    with Session(engine) as session:
        s = session.get(Student, student_id)
        if not s:
            raise HTTPException(status_code=404, detail="Student not found")
        for field in ["first_name", "last_name", "email", "major", "gpa"]:
            setattr(s, field, getattr(data, field))
        session.add(s)
        session.commit()
        session.refresh(s)
        return s

@app.delete("/students/{student_id}", status_code=204)
def delete_student(student_id: int):
    with Session(engine) as session:
        s = session.get(Student, student_id)
        if not s:
            raise HTTPException(status_code=404, detail="Student not found")
        session.delete(s)
        session.commit()
        return None

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)