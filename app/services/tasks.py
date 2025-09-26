from sqlalchemy.orm import Session

from app.models import Project, Task
from app.enums import Role, Status


def generated_task_key(db: Session, project: Project) -> str:
    tasks_count = db.query(Task).filter(Task.project_id == project.id).count()

    generated_name = project.key + "-" + str(tasks_count + 1)

    return generated_name


class TaskTransitionValidator:
    
    allowed_transitions = {
        Status.TODO: {
            Status.IN_PROGRESS: [Role.developer]
        },
        Status.IN_PROGRESS:{
            Status.READY_FOR_TESTING : [Role.developer]
        },
        Status.READY_FOR_TESTING: {
            Status.DONE : [Role.tester],
            Status.TODO: [Role.tester] # testdan o'ta olmasa qaytariladi
        },
        Status.DONE: {} # DONE bo'lsa status boshqa o'zgarmaydi
    }

    @classmethod
    def can_move(cls, old_status: Status, new_status: Status, role: Role) -> bool:
        return role in cls.allowed_transitions.get(old_status, {}).get(new_status, [])
