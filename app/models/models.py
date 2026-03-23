import uuid
from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, Text, ARRAY, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base


class Member(Base):
    __tablename__ = "members"

    uuid = Column(Text, primary_key=True)           # text, not UUID type
    member_id = Column(Text, unique=True, nullable=False)
    email = Column(Text, unique=True, nullable=False)
    fullname = Column(Text, nullable=False)
    age = Column(Integer)
    gender = Column(Text)
    dob = Column(Date)
    location = Column(Text)
    phone_number = Column(Text)
    profession = Column(Text)
    place_of_profession = Column(Text)
    department = Column(ARRAY(Text))
    volunteered_before = Column(Text)
    acknowledgement = Column(Boolean)
    can_attend_events = Column(Boolean)
    government_id_picture = Column(Text)
    member_picture = Column(Text)
    joining_date = Column(Date)
    is_admin = Column(Boolean, default=False)

    admin = relationship("Admin", back_populates="member", uselist=False)


class Admin(Base):
    __tablename__ = "admins"

    admin_id = Column(Text, primary_key=True)       # text, not UUID type
    member_id = Column(Text, ForeignKey("members.member_id", ondelete="CASCADE"), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    created_at = Column(DateTime)                   # no timezone, matches your DB

    member = relationship("Member", back_populates="admin")


class Key(Base):
    __tablename__ = "keys"

    key_name = Column(String(100), primary_key=True)
    key_value = Column(String(150), nullable=False)