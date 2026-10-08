from .models import AuditLog


def create_audit_log(
    *,
    user,
    action,
    project=None,
    task=None,
    details=None,
):
    return AuditLog.objects.create(
        user=user,
        action=action,
        project=project,
        task=task,
        details=details or {},
    )