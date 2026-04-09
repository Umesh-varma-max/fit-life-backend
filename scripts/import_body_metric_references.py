"""Import BMI/BFP reference datasets stored inside the repo."""

from __future__ import annotations

import csv
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import create_app
from extensions import db
from models.body_metric_reference import BodyMetricReference


DATA_DIR = ROOT_DIR / 'data'


def _clean_gender(value: str) -> str:
    return (value or '').strip().title()


def _to_float(row: dict, key: str):
    value = row.get(key)
    if value in (None, ''):
        return None
    return float(value)


def _to_int(row: dict, key: str):
    value = row.get(key)
    if value in (None, ''):
        return None
    return int(float(value))


def import_csv(path: Path, source: str):
    if source == 'bmi_reference':
        BodyMetricReference.query.delete()
        db.session.commit()

    BodyMetricReference.query.filter_by(source=source).delete()
    db.session.commit()

    rows_added = 0
    with path.open('r', encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            db.session.add(BodyMetricReference(
                source=source,
                gender=_clean_gender(row.get('Gender')),
                age=_to_int(row, 'Age') or 0,
                height_m=_to_float(row, 'Height') or 0,
                weight_kg=_to_float(row, 'Weight') or 0,
                bmi=_to_float(row, 'BMI') or 0,
                bmi_case=(row.get('BMIcase') or '').strip(),
                body_fat_percentage=_to_float(row, 'Body Fat Percentage'),
                body_fat_case=(row.get('BFPcase') or '').strip() or None,
                recommendation_plan=_to_int(row, 'Exercise Recommendation Plan') or 0
            ))
            rows_added += 1

    db.session.commit()
    return rows_added


def main():
    app = create_app()
    with app.app_context():
        bmi_count = import_csv(DATA_DIR / 'final_dataset.csv', 'bmi_reference')
        bfp_count = import_csv(DATA_DIR / 'final_dataset_BFP.csv', 'bfp_reference')
        print(f'Imported {bmi_count} BMI rows and {bfp_count} BFP rows.')


if __name__ == '__main__':
    main()
