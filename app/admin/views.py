from typing import List, ClassVar

from starlette_admin.contrib.sqla import ModelView
from starlette_admin.fields import EnumField, PasswordField

from app.utils import hashed_password
from app.enums import Role, Status, Priority


class UserAdminView(ModelView):
    fields: ClassVar[List[str]] = [
        "id",
        "email",
        PasswordField("hashed_password"),
        "fullname",
        # ImageField("avatar"),
        EnumField("role", enum=Role),
        "is_active",
        "is_deleted",
        "created_at",
        "updated_at",
    ]

    exclude_fields_from_list: ClassVar[List[str]] = [
        "hashed_password",
        "created_at",
        "updated_at",
    ]
    exclude_fields_from_detail: ClassVar[List[str]] = ["hashed_password"]
    exclude_fields_from_create: ClassVar[List[str]] = ["created_at", "updated_at"]
    exclude_fields_from_edit: ClassVar[List[str]] = ["created_at", "updated_at"]
    export_fields: ClassVar[List[str]] = ["id", "email", "fullname", "is_active"]
    export_types: ClassVar[List[str]] = ["csv", "excel", "pdf", "print"]

    async def create(self, request, data):
        if "hashed_password" in data:
            data["hashed_password"] = hashed_password(data["hashed_password"])

        # print("Create is working!")
        # print("=================", "avatar" in data, data['avatar'])

        # if "avatar" in data:
        #     avatar_file, should_be_deleted = data["avatar"]

        #     if avatar_file and avatar_file.filename and not should_be_deleted:
        #         avatar_filename = await self._handle_avatar_upload(avatar_file)
        #         data["avatar"] = (avatar_filename, should_be_deleted)
        #     else:
        #         data["avatar"] = (None, should_be_deleted)

        return await super().create(request, data)

    # async def _handle_avatar_upload(self, file: UploadFile) -> str | None:
    #     """Handle avatar file upload and return filename"""
    #     file_orginal_name = os.path.splitext(file.filename)[0]
    #     file_ext = os.path.splitext(file.filename)[1]

    #     file_name = f"{file_orginal_name}-{str(uuid4())[0:8]}{file_ext}"
    #     file_path = MEDIA_PATH / file_name

    #     with file_path.open("wb") as buffer:
    #         shutil.copyfileobj(file.file, buffer)

    #     return file_name


class ProjectAdminView(ModelView):
    fields: ClassVar[List[str]] = [
        "id",
        "name",
        "description",
        "key",
        "owner",
        "is_active",
        "is_private",
        "created_at",
        "updated_at",
    ]

    exclude_fields_from_list: ClassVar[List[str]] = [
        "description",
        "created_at",
        "updated_at",
    ]
    exclude_fields_from_create: ClassVar[List[str]] = [
        "key",
        "created_at",
        "updated_at",
    ]
    exclude_fields_from_edit: ClassVar[List[str]] = ["created_at", "updated_at"]
    export_fields: ClassVar[List[str]] = [
        "id",
        "name",
        "description",
        "key",
        "owner",
        "is_active",
        "is_private",
        "created_at",
        "updated_at",
    ]
    export_types: ClassVar[List[str]] = ["csv", "excel", "pdf", "print"]


class ProjectMemberAdminView(ModelView):
    fields: ClassVar[List[str]] = ["id", "user", "project", "joined_at"]

    exclude_fields_from_list: ClassVar[List[str]] = ["joined_at"]
    exclude_fields_from_create: ClassVar[List[str]] = ["joined_at"]
    exclude_fields_from_edit: ClassVar[List[str]] = ["joined_at"]
    export_fields: ClassVar[List[str]] = ["id", "user", "project", "joined_at"]
    export_types: ClassVar[List[str]] = ["csv", "excel", "pdf", "print"]


class TaskAdminView(ModelView):
    fields: ClassVar[List[str]] = [
        "id",
        "project",
        "key",
        "summary",
        "description",
        EnumField("status", enum=Status),
        EnumField("priority", enum=Priority),
        "assignee",
        "reporter",
        "due_date",
    ]

    exclude_fields_from_list: ClassVar[List[str]] = ["summary", "description"]
    export_fields: ClassVar[List[str]] = [
        "id",
        "project",
        "key,summary",
        "description",
        "status",
        "priority",
        "assignee",
        "reporter",
        "due_date",
    ]
    export_types: ClassVar[List[str]] = ["csv", "excel", "pdf", "print"]


class CommentAdminView(ModelView):
    fields: ClassVar[list[str]] = [
        "id",
        "task",
        "user",
        "content",
        "created_at",
        "updated_at",
    ]
    exclude_fields_from_list: ClassVar[list[str]] = ["created_at", "updated_at"]
    exclude_fields_from_create: ClassVar[list[str]] = ["created_at", "updated_at"]
    exclude_fields_from_edit: ClassVar[list[str]] = ["created_at", "updated_at"]
    export_fields: ClassVar[list[str]] = [
        "id",
        "task",
        "user",
        "content",
        "created_at",
        "updated_at",
    ]
    export_types: ClassVar[list[str]] = ["csv", "excel", "pdf", "print"]


class NotificationAdminView(ModelView):
    fields: ClassVar[list[str]] = [
        "id",
        "recipient",
        "sender",
        "task",
        "project",
        "message",
        "is_read",
        "created_at",
        "updated_at",
    ]
    exclude_fields_from_list: ClassVar[list[str]] = ["created_at", "updated_at"]
    exclude_fields_from_create: ClassVar[list[str]] = ["created_at", "updated_at"]
    exclude_fields_from_edit: ClassVar[list[str]] = ["created_at", "updated_at"]
    export_fields: ClassVar[list[str]] = [
        "id",
        "recipient_id",
        "sender_id",
        "task_id",
        "project_id",
        "message",
        "is_read",
        "created_at",
        "updated_at",
    ]
    export_types: ClassVar[list[str]] = ["csv", "excel", "pdf", "print"]


class AuditLogAdminView(ModelView):
    fields: ClassVar[list[str]] = [
        "id",
        "user",
        "task",
        "action",
        "timestamp",
    ]
    exclude_fields_from_list: ClassVar[list[str]] = ["task_id", "timestamp"]
    exclude_fields_from_create: ClassVar[list[str]] = ["timestamp"]
    exclude_fields_from_edit: ClassVar[list[str]] = ["timestamp"]
    export_fields: ClassVar[list[str]] = [
        "id",
        "user_id",
        "task_id",
        "action",
        "created_at",
        "updated_at",
    ]
    export_types: ClassVar[list[str]] = ["csv", "excel", "pdf", "print"]
