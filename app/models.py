from typing import List
from app.database import Base

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean, ForeignKey, DateTime, func, Text


class TimestampMixin:
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), default=func.now(),
        onupdate=func.now()
    )


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    fullname: Mapped[str] = mapped_column(String(100), nullable=True)
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_delated: Mapped[bool] = mapped_column(Boolean, default=False)

    # 🧩 One-to-many relationship: User -> Projects
    projects: Mapped[List["Project"]] = relationship(
        back_populates="owner"
    )

    def __str__(self):
        return f"User(email={self.email})"


class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    key: Mapped[str] = mapped_column(String(10), nullable=True)

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id" , ondelete="CASCADE"))
    # 🧩 Many-to-one relationship: Project -> User
    owner: Mapped["User"] = relationship(
        back_populates="projects"
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_private: Mapped[bool] = mapped_column(Boolean, default=False)

    def __str__(self):
        return f"Project(key={self.key})"


class ProjectMemmber(Base):
    __tablename__ = "project_members"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    joined_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=func.now())

    def __str__(self):
        return f"ProjectMember(user_id={self.user_id}, project_id={self.project_id})"
    

class Status(Base):
    __tablename__ = "statuses"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    def __str__(self):
        return f"Status(name={self.name})"


class Task(Base, TimestampMixin):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(20), nullable=False)
    summary: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    priority: Mapped[str] = mapped_column(String(10), nullable=False)
    due_date: Mapped[DateTime] = mapped_column(DateTime(timezone=True))

    project_id: Mapped[int] = mapped_column(Integer,
                                    ForeignKey("projects.id", ondelete="CASCADE"))
    status_id: Mapped[int] = mapped_column(Integer, 
                                    ForeignKey("statuses.id", ondelete="CASCADE"))
    assignee_id: Mapped[int] = mapped_column(Integer,
                                    ForeignKey("users.id", ondelete="CASCADE"))
    reporter_id: Mapped[int] = mapped_column(Integer, 
                                    ForeignKey("users.id", ondelete="CASCADE"))
    

    def __str__(self):
        return f"Task(summary={self.summary})"


class Comment(Base, TimestampMixin):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(Integer,
                            ForeignKey("tasks.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(Integer,
                            ForeignKey("users.id", ondelete="CASCADE"))
    content: Mapped[str] = mapped_column(Text, nullable=False)


    def __str__(self):
        return f"Comment(task_id={self.task_id}, user_id={self.user_id})"


class Notification(Base, TimestampMixin):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)

    recipient_id: Mapped[int] = mapped_column(Integer,
                                ForeignKey("users.id", ondelete="CASCADE"))
    sender_id: Mapped[int] = mapped_column(Integer,
                                ForeignKey("users.id", ondelete="CASCADE"))
    task_id: Mapped[int] = mapped_column(Integer,
                                ForeignKey("tasks.id", ondelete="CASCADE"))
    project_id: Mapped[int] = mapped_column(Integer, 
                                ForeignKey("projects.id", onupdate="CASCADE"))


    def __str__(self):
        return f"Notification(user_id={self.recipient_id})"


class AuditLog(Base):
    __tablename__ = "auditlogs"

    id: Mapped[int] = mapped_column(primary_key=True)
    action: Mapped[str] = mapped_column(String(250), nullable=False)
    timestamp: Mapped[DateTime] = mapped_column(DateTime(timezone=True),
                                default=func.now())
    
    user_id: Mapped[int] = mapped_column(Integer,
                            ForeignKey("users.id", ondelete='CASCADE'))
    task_id: Mapped[int] = mapped_column(Integer,
                            ForeignKey("tasks.id", ondelete="CASCADE"))
    

    def __str__(self):
        return f"AuditLog(user_id={self.user_id})"





