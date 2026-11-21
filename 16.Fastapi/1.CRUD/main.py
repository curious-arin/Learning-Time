from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel, Field, EmailStr, field_validator, computed_field
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()

# CORS -> Cross Origin Resource Sharing
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_headers=["*"], allow_methods=["*"])


"""
GET: only shows message
"""


@app.get("/")  # endpoint-> where on the url message must be displayed
def greet():
    return {"Welcome back Arin"}


# Helper Functions
@app.get("/students")
def load_data():
    with open("data.json", "r") as file:
        return json.load(file)


def save_data(data):
    with open("data.json", "w") as file:
        json.dump(data, file, indent=4)


# Gets a student based on id along with exception handling
@app.get("/students/{id}")
def get_id(id: str = Path(..., description="id endpoint", examples=["S001"])):
    data = load_data()

    if id not in data:
        raise HTTPException(status_code=405, detail="Student does not exists!")

    return data[id]


# Filters student based on course
@app.get("/filter")
def filter_student(
    course: str = Query(
        None, description="filters students based on course", examples=["data science"]
    )
):
    data = load_data()

    if not course:
        return data

    filtered = {}
    for id, student in data.items():
        if student["course"].lower() == course.lower():
            filtered[id] = student
    return filtered


# Sorts students by name, age & marks
sort_field = ["name", "age", "marks"]
sort_order = ["asc", "desc"]


@app.get("/sort")
def sort_students(
    sort_by: str = Query(
        None, description="sort by name, age, marks", examples=["name"]
    ),
    order: str = Query(None, description="sort by asc, desc", examples=["asc"]),
):
    # error message when invalid field is added
    if sort_by not in sort_field:
        raise HTTPException(
            status_code=404, detail=f"invalid input, choose from {sort_field}"
        )
    # error message when invalid order is added
    if order not in sort_order:
        raise HTTPException(
            status_code=404, detail=f"invalid order, choose from {sort_order}"
        )

    data = load_data()

    # Turn the dictionary into a list, putting the ID inside each student
    profile = []
    for id, student in data.items():
        student["id"] = id
        profile.append(student)

    # Sort by marks
    reverse = order == "desc"
    sorted_students = sorted(
        profile, key=lambda choice: choice[sort_by], reverse=reverse
    )
    return sorted_students


# Splitting data into pages
@app.get("/pagination")
def paginate(
    page: int = Query(1, ge=1, description="Input page number"),
    limit: int = Query(2, ge=1, le=100, description="Input limit"),
):
    data = load_data()

    # Turn the dictionary into a list, putting the ID inside each student
    profile = []
    for id, student in data.items():
        student["id"] = id
        profile.append(student)

    start = (page - 1) * limit
    end = start + limit

    student_page = profile[start:end]
    total_student = len(profile)
    return {
        "page": page,
        "limit": limit,
        "total students": total_student,
        "students": student_page,
    }


"""
Post :  Accepts, validates, and parses incoming JSON data from a client
"""


class Student(BaseModel):  # pydantic model
    id: str = Field(..., min_length=2, examples=["S001"])
    name: str = Field(..., min_length=2, max_length=50)  # ... means required field
    age: int = Field(..., gt=0, le=122)
    email: EmailStr
    course: str = Field(..., max_length=50)
    marks: int = Field(..., gt=0, le=100)

    # Custom rule: Name must contain only letters and spaces
    @field_validator("name")
    @classmethod
    def check_name(cls, value):
        if not value.replace(" ", "").isalpha():
            raise ValueError("Name must contain only letters and spaces")
        return value.title()

    # Computed Field
    @computed_field
    @property
    def grade(self) -> str:
        if self.marks >= 90:
            return "A+"
        elif self.marks >= 80:
            return "A"
        elif self.marks >= 70:
            return "B"
        elif self.marks >= 60:
            return "C"
        else:
            return "F"


@app.post("/create", status_code=201)
def create_student(student: Student):
    data = load_data()

    if student.id in data:
        raise HTTPException(
            status_code=400, detail=f"Student with id {student.id} already exists!"
        )
    data[student.id] = student.model_dump(exclude={"id", "grade"})
    save_data(data)

    return {f"message: {student.name} registered successfully!"}


"""
PUT: updates or replaces an existing resource
"""


class StudentUpdate(BaseModel):  # pydantic model
    id: str | None = Field(None, min_length=2, examples=["S001"])
    name: str | None = Field(
        None, min_length=2, max_length=50
    )  # ... means required field
    age: int | None = Field(None, gt=0, le=122)
    email: EmailStr | None = None
    course: str | None = Field(None, max_length=50)
    marks: int | None = Field(None, gt=0, le=100)


@app.put("/students/{student_id}")
def update_student(
    student_update: StudentUpdate,
    student_id: str = Path(..., description="Student ID", examples=["S001"]),
):
    data = load_data()

    if student_id not in data:
        raise HTTPException(
            status_code=404, detail=f"Student with id {student_id} does not exist"
        )

    # The student as it is right now
    existing = data[student_id]

    # only the field the client actually sent
    update = student_update.model_dump(exclude_unset=True)

    # Copy the new value on the top of old one
    for key, value in update.items():
        existing[key] = value

    # Checks the final student again
    student = Student(**existing)

    data[student_id] = student.model_dump(exclude={"id", "grade"})
    
    save_data(data)

    return {f"message: {student.name} updated successfully!"}


"""
DELETE: deletes or removes an existing source
"""


@app.delete("/delete/{student_id}")
def update_student(
    student_id: str = Path(..., description="Student ID", examples=["S001"]),
):
    data = load_data()

    if student_id not in data:
        raise HTTPException(
            status_code=404, detail=f"Student with id {student_id} does not exist"
        )

    del data[student_id]
    save_data(data)

    return {f"message: {student_id} deleted successfully!"}
