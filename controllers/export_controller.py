# controllers/export_controller.py
from flask import Response
from models.health_profile import HealthProfile
from models.activity_log import ActivityLog
from utils.pdf_generator import generate_health_report
from datetime import date, timedelta


def export_pdf(user):
    """Generate and return PDF health report."""
    profile = HealthProfile.query.filter_by(user_id=user.id).first()

    # Get last 7 days of activity logs
    week_ago = date.today() - timedelta(days=7)
    logs = ActivityLog.query.filter(
        ActivityLog.user_id == user.id,
        ActivityLog.log_date >= week_ago
    ).order_by(ActivityLog.log_date.desc()).all()

    pdf_bytes = generate_health_report(user, profile, logs)

    return Response(
        pdf_bytes,
        mimetype='application/pdf',
        headers={
            'Content-Disposition': 'attachment; filename=fitlife-health-report.pdf'
        }
    )
