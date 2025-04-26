from sqlalchemy import String, Integer, ForeignKey, Boolean, DateTime, Double
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.db import Base
from datetime import datetime 


class Category(Base):
    __tablename__ = 'type_mero'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name_category: Mapped[str] = mapped_column(String(50))
    max_peoples: Mapped[int] = mapped_column(Integer)
    commands: Mapped[list["RegCommand"]] = relationship(back_populates="category")

    def __repr__(self):
        return f"<Category(id={self.id}, name_category='{self.name_category}', max_peoples={self.max_peoples})>"
    

class RegCommand(Base):
    __tablename__ = 'reg_commands'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    command_name: Mapped[str] = mapped_column(String)
    category_id: Mapped[int] = mapped_column(ForeignKey("type_mero.id"))
    category: Mapped["Category"] = relationship(back_populates="commands")
    members: Mapped[list["Member"]] = relationship(back_populates="command", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<RegCommand(id={self.id}, command_name='{self.command_name}', category_id={self.category_id})>"


class Users(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_name: Mapped[str] = mapped_column(String)
    user_tg: Mapped[str] = mapped_column(String, unique=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    score: Mapped[float] = mapped_column(Double, default=0.0)
    username_tg: Mapped[str] = mapped_column(String)

    registrations: Mapped[list["LectureRegistrations"]] = relationship(back_populates="user")

    def __repr__(self):
        return f"<Users(id={self.id}, user_name='{self.user_name}', user_tg='{self.user_tg}')>"


class Member(Base):
    __tablename__ = 'members'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    telegram: Mapped[str] = mapped_column(String, nullable=False)
    command_id: Mapped[int] = mapped_column(ForeignKey("reg_commands.id"))
    command: Mapped["RegCommand"] = relationship(back_populates="members")

    def __repr__(self):
        return f"<Member(id={self.id}, first_name='{self.first_name}', last_name='{self.last_name}', telegram='{self.telegram}', command_id={self.command_id})>"


class Lectures(Base):
    __tablename__ = 'lectures'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    speaker: Mapped[str] = mapped_column(String(100), nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    max_seats: Mapped[int] = mapped_column(Integer, nullable=False)
    format: Mapped[str] = mapped_column(String(10), nullable=False)  # "online" или "offline"
    conference_link: Mapped[str] = mapped_column(String(255), nullable=True)
    offline_map_link: Mapped[str] = mapped_column(String(255), nullable=True)
    offline_photo: Mapped[str] = mapped_column(String(255), nullable=True)

    registrations: Mapped[list["LectureRegistrations"]] = relationship(back_populates="lecture")

    def __repr__(self):
        return f"<Lectures(id={self.id}, title='{self.title}', speaker='{self.speaker}', date={self.date}, format={self.format})>"


class LectureRegistrations(Base):
    __tablename__ = 'lecture_registrations'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    lecture_id: Mapped[int] = mapped_column(ForeignKey("lectures.id"), nullable=False)

    user: Mapped["Users"] = relationship(back_populates="registrations")
    lecture: Mapped["Lectures"] = relationship(back_populates="registrations")

    def __repr__(self):
        return f"<LectureRegistrations(id={self.id}, user_id={self.user_id}, lecture_id={self.lecture_id})>"