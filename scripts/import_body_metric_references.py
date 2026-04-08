import csv
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app import create_app
from extensions import db
from models.body_metric_reference import BodyMetricReference


def _float_or_none(value):
    if value in (None, ''):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _int_or_none(value):
    if value in (None, ''):
        return None
    try:
        return int(float(value))
    except ValueError:
        return None


def import_csv(path: Path, source_dataset: str):
    created = 0
    with path.open('r', encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            db.session.add(BodyMetricReference(
                source_dataset=source_dataset,
                weight=_float_or_none(row.get('Weight')),
                height=_float_or_none(row.get('Height')),
                bmi=_float_or_none(row.get('BMI')),
                body_fat_percentage=_float_or_none(row.get('Body Fat Percentage')),
                category=(row.get('BFPcase') or row.get('BMIcase') or '').strip() or None,
                gender=(row.get('Gender') or '').strip() or None,
                age=_int_or_none(row.get('Age')),
                bmi_case=(row.get('BMIcase') or '').strip() or None,
                exercise_recommendation_plan=_int_or_none(row.get('Exercise Recommendation Plan'))
            ))
            created += 1
    return created


if __name__ == '__main__':
    app = create_app()
    base_dir = Path(r'C:\Users\rajus\OneDrive\Desktop\archive')
    bmi_path = base_dir / 'final_dataset.csv'
    bfp_path = base_dir / 'final_dataset_BFP .csv'

    with app.app_context():
        BodyMetricReference.query.delete()
        created_bmi = import_csv(bmi_path, 'bmi')
        created_bfp = import_csv(bfp_path, 'bfp')
        db.session.commit()
        print(f'Imported {created_bmi} BMI rows and {created_bfp} BFP rows.')
