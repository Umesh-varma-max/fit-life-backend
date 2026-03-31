# utils/pdf_generator.py
"""
PDF health report generator using fpdf2.
Generates a styled health report with body metrics and weekly activity summary.
"""

from fpdf import FPDF
from datetime import date, timedelta


def generate_health_report(user, profile, activity_logs) -> bytes:
    """
    Generate a PDF health report for the user.

    Args:
        user: User model instance
        profile: HealthProfile model instance (can be None)
        activity_logs: list of ActivityLog entries for the past 7 days

    Returns:
        PDF file as bytes
    """
    pdf = FPDF()
    pdf.add_page()

    # ─── Header ───────────────────────────────────────────
    pdf.set_fill_color(0, 212, 170)  # Accent color #00d4aa
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_font('Helvetica', 'B', 22)
    pdf.set_text_color(255, 255, 255)
    pdf.set_y(10)
    pdf.cell(0, 10, 'FitLife Health Report', align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.set_font('Helvetica', '', 12)
    pdf.cell(0, 8, f'{user.full_name} | {date.today().strftime("%B %d, %Y")}', align='C', new_x='LMARGIN', new_y='NEXT')

    # ─── Body Metrics ─────────────────────────────────────
    pdf.set_y(50)
    pdf.set_text_color(40, 40, 60)
    pdf.set_font('Helvetica', 'B', 16)
    pdf.cell(0, 10, 'Body Metrics', new_x='LMARGIN', new_y='NEXT')
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)

    pdf.set_font('Helvetica', '', 12)
    if profile:
        metrics = [
            ('BMI', f"{float(profile.bmi):.1f}" if profile.bmi else '—'),
            ('Weight', f"{float(profile.weight_kg):.1f} kg" if profile.weight_kg else '—'),
            ('Height', f"{float(profile.height_cm):.1f} cm" if profile.height_cm else '—'),
            ('Fitness Goal', (profile.fitness_goal or '—').replace('_', ' ').title()),
            ('Activity Level', (profile.activity_level or '—').title()),
            ('Daily Calorie Target', f"{profile.daily_calories or '—'} kcal"),
        ]
        for label, value in metrics:
            pdf.set_font('Helvetica', 'B', 11)
            pdf.cell(60, 8, f'{label}:', new_x='RIGHT')
            pdf.set_font('Helvetica', '', 11)
            pdf.cell(0, 8, str(value), new_x='LMARGIN', new_y='NEXT')
    else:
        pdf.cell(0, 8, 'No profile data available.', new_x='LMARGIN', new_y='NEXT')

    # ─── Weekly Summary ───────────────────────────────────
    pdf.ln(10)
    pdf.set_font('Helvetica', 'B', 16)
    pdf.cell(0, 10, 'Last 7 Days Summary', new_x='LMARGIN', new_y='NEXT')
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)

    total_cal_in  = sum(l.calories_in or 0 for l in activity_logs)
    total_cal_out = sum(l.calories_out or 0 for l in activity_logs)
    total_water   = sum(l.water_ml or 0 for l in activity_logs)
    workout_days  = len(set(
        l.log_date for l in activity_logs if l.log_type == 'workout'
    ))

    summary = [
        ('Total Calories Consumed', f"{total_cal_in} kcal"),
        ('Total Calories Burned', f"{total_cal_out} kcal"),
        ('Net Calories', f"{total_cal_in - total_cal_out} kcal"),
        ('Total Water Intake', f"{total_water} ml"),
        ('Workout Days', str(workout_days)),
    ]

    pdf.set_font('Helvetica', '', 11)
    for label, value in summary:
        pdf.set_font('Helvetica', 'B', 11)
        pdf.cell(60, 8, f'{label}:', new_x='RIGHT')
        pdf.set_font('Helvetica', '', 11)
        pdf.cell(0, 8, str(value), new_x='LMARGIN', new_y='NEXT')

    # ─── Activity Log Table ───────────────────────────────
    pdf.ln(10)
    pdf.set_font('Helvetica', 'B', 16)
    pdf.cell(0, 10, 'Activity Log Details', new_x='LMARGIN', new_y='NEXT')
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)

    if activity_logs:
        # Table header
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_fill_color(240, 244, 248)
        pdf.cell(25, 8, 'Date', border=1, fill=True)
        pdf.cell(25, 8, 'Type', border=1, fill=True)
        pdf.cell(60, 8, 'Description', border=1, fill=True)
        pdf.cell(25, 8, 'Cal In', border=1, fill=True)
        pdf.cell(25, 8, 'Cal Out', border=1, fill=True)
        pdf.cell(25, 8, 'Water', border=1, fill=True, new_x='LMARGIN', new_y='NEXT')

        # Table rows
        pdf.set_font('Helvetica', '', 9)
        for log in activity_logs[:30]:  # Limit to 30 rows for PDF size
            pdf.cell(25, 7, str(log.log_date), border=1)
            pdf.cell(25, 7, log.log_type or '', border=1)
            desc = (log.description or '')[:30]
            pdf.cell(60, 7, desc, border=1)
            pdf.cell(25, 7, str(log.calories_in or 0), border=1)
            pdf.cell(25, 7, str(log.calories_out or 0), border=1)
            pdf.cell(25, 7, f"{log.water_ml or 0}ml", border=1, new_x='LMARGIN', new_y='NEXT')
    else:
        pdf.set_font('Helvetica', '', 11)
        pdf.cell(0, 8, 'No activity data for this period.', new_x='LMARGIN', new_y='NEXT')

    # ─── Footer ───────────────────────────────────────────
    pdf.ln(15)
    pdf.set_font('Helvetica', 'I', 9)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 8, 'Generated by FitLife AI Fitness Management System', align='C')

    return pdf.output()
