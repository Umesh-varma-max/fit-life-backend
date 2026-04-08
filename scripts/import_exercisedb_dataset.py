import argparse
import json
from pathlib import Path
import sys

import requests

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app import create_app
from extensions import db
from models.exercise_library import ExerciseLibrary

FREE_EXERCISE_DB_IMAGE_PREFIX = "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises/"


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

    with db.session.no_autoflush:
        exercise = ExerciseLibrary.query.filter_by(external_id=external_id).first()
    if not exercise:
        exercise = ExerciseLibrary(external_id=external_id)
        db.session.add(exercise)

    exercise.name = record.get('name') or exercise.name or external_id
    exercise.body_parts = _ensure_list(record.get('bodyParts') or record.get('body_parts') or record.get('bodyParts'))
    exercise.target_muscles = _ensure_list(record.get('targetMuscles') or record.get('target_muscles') or record.get('primaryMuscles'))
    exercise.secondary_muscles = _ensure_list(record.get('secondaryMuscles') or record.get('secondary_muscles'))
    exercise.equipments = _ensure_list(record.get('equipments') or record.get('equipment'))
    exercise.keywords = _ensure_list(record.get('keywords') or record.get('primaryMuscles') or record.get('category'))
    exercise.instructions = _ensure_list(record.get('instructions'))
    exercise.exercise_tips = _ensure_list(record.get('exerciseTips') or record.get('tips'))
    exercise.variations = _ensure_list(record.get('variations'))
    exercise.related_exercise_ids = _ensure_list(record.get('relatedExerciseIds'))
    exercise.gender = record.get('gender')
    exercise.exercise_type = record.get('exerciseType') or record.get('exercise_type') or record.get('category')
    exercise.overview = record.get('overview') or (
        f"{exercise.name} is a {record.get('level', 'general')} {record.get('category', 'fitness')} exercise "
        f"primarily targeting {', '.join(exercise.target_muscles[:2]) or 'multiple muscle groups'}."
    )

    images = _ensure_list(record.get('images'))
    primary_image = images[0] if images else None
    secondary_image = images[1] if len(images) > 1 else primary_image

    if primary_image and not str(primary_image).startswith('http'):
        primary_image = f"{FREE_EXERCISE_DB_IMAGE_PREFIX}{primary_image}"
    if secondary_image and not str(secondary_image).startswith('http'):
        secondary_image = f"{FREE_EXERCISE_DB_IMAGE_PREFIX}{secondary_image}"

    exercise.image_url = record.get('imageUrl') or record.get('image_url') or primary_image
    exercise.gif_url = record.get('gifUrl') or record.get('gif_url')
    exercise.video_url = record.get('videoUrl') or record.get('video_url') or secondary_image
    exercise.source = record.get('source') or 'free-exercise-db'
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


def _load_records_from_rapidapi(url: str, api_key: str, host: str):
    headers = {
        'Content-Type': 'application/json',
        'X-RapidAPI-Key': api_key,
        'X-RapidAPI-Host': host
    }
    response = requests.get(url, headers=headers, timeout=120)
    response.raise_for_status()
    payload = response.json()
    return payload if isinstance(payload, list) else payload.get('data', payload.get('results', []))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Import ExerciseDB-style exercise records into FitLife.')
    parser.add_argument('--json-path', help='Path to a local ExerciseDB JSON export.')
    parser.add_argument('--url', help='HTTP endpoint that returns a JSON exercise array.')
    parser.add_argument('--api-key', help='Optional bearer token for the HTTP endpoint.')
    parser.add_argument('--rapidapi-key', help='RapidAPI key for ExerciseDB-style endpoints.')
    parser.add_argument('--rapidapi-host', help='RapidAPI host header value.')
    parser.add_argument('--clear', action='store_true', help='Delete existing exercise records before import.')
    args = parser.parse_args()

    if not args.json_path and not args.url:
        parser.error('Provide either --json-path or --url')
    if args.rapidapi_key and not args.rapidapi_host:
        parser.error('Provide --rapidapi-host with --rapidapi-key')

    app = create_app()
    with app.app_context():
        if args.clear:
            db.session.query(ExerciseLibrary).delete()
            db.session.commit()

        if args.json_path:
            records = _load_records_from_file(Path(args.json_path))
        elif args.rapidapi_key:
            records = _load_records_from_rapidapi(args.url, args.rapidapi_key, args.rapidapi_host)
        else:
            records = _load_records_from_url(args.url, args.api_key)
        imported = 0
        for index, record in enumerate(records, start=1):
            if _upsert_exercise(record):
                imported += 1
            if index % 200 == 0:
                db.session.flush()

        db.session.commit()
        print(f'Imported or updated {imported} exercise records.')
