from pydantic import BaseModel, Field, EmailStr, field_validator, computed_field
import json

class Student(BaseModel): # pydantic model
    id: str = Field(..., min_length=2, examples=["S001"])
    name: str = Field(..., min_length=2, max_length=50) # ... means required field
    age: int = Field(..., gt=0, le=122)
    email : EmailStr
    marks : int = Field(..., gt=0, le=100)
    course : str = Field(..., max_length=50)
    phone : str | None = None

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


s = Student(id="S001", name="abhinav singh", age=22, email="abhinavsingh@gmail.com", marks=89, course="Data science", phone="")
data = s.model_dump()


with open("data.json", "r") as file:
    loaded_data = json.load(file)

for student_id, info in loaded_data.items():
    s = Student(id=student_id, **info)
    print(s.id, s.name, s.grade, s.email)