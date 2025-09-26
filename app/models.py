from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func

from app.database import Base


class TimestampMixin:
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
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
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )

    owned_projects: Mapped[List["Project"]] = relationship(
        "Project", back_populates="owner"
    )

    member_projects: Mapped[List["ProjectMember"]] = relationship(
        "ProjectMember", back_populates="user"
    )

    comments: Mapped[List["Comment"]] = relationship("Comment", back_populates="user")

    assigned_tasks: Mapped[List["Task"]] = relationship(
        "Task", back_populates="assignee", foreign_keys="Task.assignee_id"
    )

    reported_tasks: Mapped[List["Task"]] = relationship(
        "Task", back_populates="reporter", foreign_keys="Task.reporter_id"
    )

    received_notifications: Mapped[List["Notification"]] = relationship(
        "Notification",
        back_populates="recipient",
        foreign_keys="Notification.recipient_id",
    )

    send_notifications: Mapped[List["Notification"]] = relationship(
        "Notification", back_populates="sender", foreign_keys="Notification.sender_id"
    )

    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog", back_populates="user"
    )

    def __str__(self):
        return f"User(email={self.email})"


class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    key: Mapped[str] = mapped_column(String(10), nullable=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_private: Mapped[bool] = mapped_column(Boolean, default=False)

    owner: Mapped["User"] = relationship("User", back_populates="owned_projects")

    members: Mapped[List["ProjectMember"]] = relationship(
        "ProjectMember", back_populates="project"
    )

    notifications: Mapped[List["Notification"]] = relationship(
        "Notification", back_populates="project"
    )

    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="project")

    def __str__(self):
        return f"Project(key={self.key})"


class ProjectMember(Base):
    __tablename__ = "project_members"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE")
    )
    joined_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), default=func.now()
    )

    project: Mapped["Project"] = relationship("Project", back_populates="members")

    user: Mapped["User"] = relationship("User", back_populates="member_projects")

    def __str__(self):
        return f"ProjectMember(user_id={self.user_id}, project_id={self.project_id})"


class Task(Base, TimestampMixin):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id", ondelete="CASCADE")
    )
    key: Mapped[str] = mapped_column(String(20), nullable=False)
    summary: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[int] = mapped_column(String(30), nullable=False) #IN_PROGRESS
    priority: Mapped[str] = mapped_column(String(10), nullable=False)
    assignee_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    reporter_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE")
    )
    due_date: Mapped[DateTime] = mapped_column(DateTime(timezone=True))

    project: Mapped["Project"] = relationship("Project", back_populates="tasks")
    assignee: Mapped["User"] = relationship(
        "User", back_populates="assigned_tasks", foreign_keys="Task.assignee_id"
    )
    reporter: Mapped["User"] = relationship(
        "User", back_populates="reported_tasks", foreign_keys="Task.reporter_id"
    )
    comments: Mapped[List["Comment"]] = relationship("Comment", back_populates="task")
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification", back_populates="task"
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog", back_populates="task"
    )

    def __str__(self):
        return f"Task(summary={self.summary})"


class Comment(Base, TimestampMixin):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tasks.id", ondelete="CASCADE")
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE")
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)

    task: Mapped["Task"] = relationship("Task", back_populates="comments")
    user: Mapped["User"] = relationship("User", back_populates="comments")

    def __str__(self):
        return f"Comment(task_id={self.task_id}, user_id={self.user_id})"


class Notification(Base, TimestampMixin):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    recipient_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE")
    )
    sender_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE")
    )
    task_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tasks.id", ondelete="CASCADE")
    )
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id", onupdate="CASCADE")
    )

    recipient: Mapped["User"] = relationship(
        "User",
        back_populates="received_notifications",
        foreign_keys="Notification.recipient_id",
    )
    sender: Mapped["User"] = relationship(
        "User",
        back_populates="send_notifications",
        foreign_keys="Notification.sender_id",
    )
    task: Mapped["Task"] = relationship("Task", back_populates="notifications")
    project: Mapped["Project"] = relationship("Project", back_populates="notifications")

    def __str__(self):
        return f"Notification(user_id={self.recipient_id})"


class AuditLog(Base):
    __tablename__ = "auditlogs"

    id: Mapped[int] = mapped_column(primary_key=True)
    action: Mapped[str] = mapped_column(String(250), nullable=False)
    timestamp: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), default=func.now()
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE")
    )
    task_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tasks.id", ondelete="CASCADE")
    )

    user: Mapped["User"] = relationship("User", back_populates="audit_logs")
    task: Mapped["Task"] = relationship("Task", back_populates="audit_logs")

    def __str__(self):
        return f"AuditLog(user_id={self.user_id})"
