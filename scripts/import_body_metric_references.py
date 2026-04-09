import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import create_app  # noqa: E402
from extensions import db  # noqa: E402
from models.body_metric_reference import BodyMetricReference  # noqa: E402


def _to_float(value):
    try:
        return float(value) if value not in (None, '') else None
    except ValueError:
        return None


def _to_int(value):
    try:
        return int(float(value)) if value not in (None, '') else None
    except ValueError:
        return None


def import_csv(csv_path: str, source_dataset: str):
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f'CSV not found: {csv_path}')

    BodyMetricReference.query.filter_by(source_dataset=source_dataset).delete(synchronize_session=False)

    inserted = 0
    with path.open('r', encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            entry = BodyMetricReference(
                source_dataset=source_dataset,
                weight=_to_float(row.get('Weight')),
                height=_to_float(row.get('Height')),
                bmi=_to_float(row.get('BMI')),
                body_fat_percentage=_to_float(row.get('Body Fat Percentage')),
                bfp_case=row.get('BFPcase'),
                gender=(row.get('Gender') or '').lower() or None,
                age=_to_int(row.get('Age')),
                bmi_case=row.get('BMIcase'),
                exercise_recommendation_plan=_to_int(row.get('Exercise Recommendation Plan')),
                raw_payload=row,
            )
            db.session.add(entry)
            inserted += 1

    db.session.commit()
    return inserted


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        data_dir = ROOT / 'data'
        datasets = [
            (data_dir / 'final_dataset.csv', 'bmi_reference'),
            (data_dir / 'final_dataset_BFP .csv', 'bfp_reference'),
        ]
        total = 0
        for csv_path, source in datasets:
            total += import_csv(csv_path, source)
        print(f'Imported {total} body metric reference rows.')
