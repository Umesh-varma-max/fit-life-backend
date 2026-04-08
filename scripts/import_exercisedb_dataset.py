import argparse
import json
from pathlib import Path
import sys

import requests

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app import create_app
from extensions import db
from models.exercise_library import ExerciseLibrary


def _ensure_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [chunk.strip() for chunk in value.split(',') if chunk.strip()]
    return [str(value).strip()]


def _upsert_exercise(record: dict):
    external_id = str(record.get('exerciseId') or record.get('id') or record.get('external_id') or '').strip()
    if not external_id:
        return False

    exercise = ExerciseLibrary.query.filter_by(external_id=external_id).first()
    if not exercise:
        exercise = ExerciseLibrary(external_id=external_id)
        db.session.add(exercise)

    exercise.name = record.get('name') or exercise.name or external_id
    exercise.body_parts = _ensure_list(record.get('bodyParts') or record.get('body_parts'))
    exercise.target_muscles = _ensure_list(record.get('targetMuscles') or record.get('target_muscles'))
    exercise.secondary_muscles = _ensure_list(record.get('secondaryMuscles') or record.get('secondary_muscles'))
    exercise.equipments = _ensure_list(record.get('equipments') or record.get('equipment'))
    exercise.keywords = _ensure_list(record.get('keywords'))
    exercise.instructions = _ensure_list(record.get('instructions'))
    exercise.exercise_tips = _ensure_list(record.get('exerciseTips') or record.get('tips'))
    exercise.variations = _ensure_list(record.get('variations'))
    exercise.related_exercise_ids = _ensure_list(record.get('relatedExerciseIds'))
    exercise.gender = record.get('gender')
    exercise.exercise_type = record.get('exerciseType') or record.get('exercise_type')
    exercise.overview = record.get('overview')
    exercise.image_url = record.get('imageUrl') or record.get('image_url')
    exercise.gif_url = record.get('gifUrl') or record.get('gif_url')
    exercise.video_url = record.get('videoUrl') or record.get('video_url')
    exercise.source = record.get('source') or 'ExerciseDB'
    return True


def _load_records_from_file(path: Path):
    raw_text = path.read_text(encoding='utf-8')
    payload = json.loads(raw_text)
    return payload if isinstance(payload, list) else payload.get('data', [])


def _load_records_from_url(url: str, api_key: str | None = None):
    headers = {}
    if api_key:
        headers['Authorization'] = f'Bearer {api_key}'
    response = requests.get(url, headers=headers, timeout=90)
    response.raise_for_status()
    payload = response.json()
    return payload if isinstance(payload, list) else payload.get('data', [])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Import ExerciseDB-style exercise records into FitLife.')
    parser.add_argument('--json-path', help='Path to a local ExerciseDB JSON export.')
    parser.add_argument('--url', help='HTTP endpoint that returns a JSON exercise array.')
    parser.add_argument('--api-key', help='Optional bearer token for the HTTP endpoint.')
    parser.add_argument('--clear', action='store_true', help='Delete existing exercise records before import.')
    args = parser.parse_args()

    if not args.json_path and not args.url:
        parser.error('Provide either --json-path or --url')

    app = create_app()
    with app.app_context():
        if args.clear:
            ExerciseLibrary.query.delete()

        records = _load_records_from_file(Path(args.json_path)) if args.json_path else _load_records_from_url(args.url, args.api_key)
        imported = 0
        for record in records:
            if _upsert_exercise(record):
                imported += 1

        db.session.commit()
        print(f'Imported or updated {imported} exercise records.')
