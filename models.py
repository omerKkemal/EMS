from sqlalchemy import String, Integer, Column, Date, ForeignKey
from flask_login import UserMixin
from db import Base

class User(UserMixin, Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    password = Column(String, index=True)
    is_default_user = Column(Integer, index=True)

    # No custom __init__ needed
    def __repr__(self):        
        return f"User(id={self.id}, email={self.email}, password={self.password}, is_default_user={self.is_default_user})"

class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    fname = Column(String, index=True)
    mname = Column(String, index=True)
    lname = Column(String, index=True)
    gender = Column(String, index=True)
    fanID = Column(String, index=True)
    birthdate = Column(Date, index=True)
    phone_number = Column(Integer, index=True)
    edu_level = Column(String, index=True)
    profession = Column(String, index=True)
    work_experience = Column(Integer, index=True)
    group_name = Column(String, index=True)
    position_in_group = Column(String, index=True)
    join_year = Column(Date, index=True)
    work_place = Column(String, index=True)
    work_place_name = Column(String, index=True)
    salary = Column(Integer, index=True)
    werada = Column(String, index=True)
    kebele = Column(String, index=True)
    house_number = Column(Integer, index=True)
    photo_url = Column(String, index=True)

    # No custom __init__ – SQLAlchemy's default constructor accepts all columns
    def __repr__(self):
        return f"Employee(id={self.id}, fname={self.fname}, mname={self.mname}, lname={self.lname}, gender={self.gender}, fanID={self.fanID}, birthdate={self.birthdate}, phone_number={self.phone_number}, edu_level={self.edu_level}, profession={self.profession}, work_experience={self.work_experience}, join_year={self.join_year}, group_name={self.group_name}, position_in_group={self.position_in_group}, work_place={self.work_place}, work_place_name={self.work_place_name}, salary={self.salary}, werada={self.werada}, kebele={self.kebele}, house_number={self.house_number}, photo_url={self.photo_url})"

class Doc(Base):
    __tablename__ = "docs"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    name = Column(String, index=True)
    url = Column(String, index=True)
    file_type = Column(String, index=True)

    # No custom __init__ needed – SQLAlchemy's default is fine
    def __repr__(self):
        return f"Doc(id={self.id}, name={self.name}, url={self.url}, file_type={self.file_type})"