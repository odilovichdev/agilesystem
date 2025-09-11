from starlette_admin.contrib.sqla import Admin

from app.database import engine
from app.admin.auth import StarletteAuthProvider
from app.models import (
    User,
    Task,
    Comment,
    Notification,
    AuditLog,
    Project,
    ProjectMember,
)
from app.admin.views import (
    UserAdminView,
    TaskAdminView,
    CommentAdminView,
    NotificationAdminView,
    AuditLogAdminView,
    ProjectAdminView,
    ProjectMemberAdminView,
)


admin = Admin(
    engine=engine,
    base_url="/admin",
    title="Agile admin",
    auth_provider=StarletteAuthProvider(login_path="/login", logout_path="/logout"),
)


admin.add_view(UserAdminView(User, icon="fa fa-user"))
admin.add_view(ProjectAdminView(Project, icon="fa fa-suitcase"))
admin.add_view(ProjectMemberAdminView(ProjectMember, icon="fa fa-user"))
admin.add_view(TaskAdminView(Task, icon="fa fa-tasks"))
admin.add_view(CommentAdminView(Comment, icon="fa fa-comment"))
admin.add_view(NotificationAdminView(Notification, icon="fa fa-bell"))
admin.add_view(AuditLogAdminView(AuditLog, icon="fa fa-history"))
