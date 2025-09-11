from sqlalchemy.orm import Session

from app.models import Project, Task


def generated_task_key(db: Session, project: Project) -> str:
    tasks_count = db.query(Task).filter(Task.project_id == project.id).count()

    generated_name = project.key + "-" + str(tasks_count + 1)

    return generated_name
