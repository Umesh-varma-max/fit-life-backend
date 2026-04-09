"""Import exercises from free-exercise-db into the exercise library table."""

from __future__ import annotations

import json
import re
from pathlib import Path
import sys

import requests

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import create_app
from extensions import db
from models.exercise_library import ExerciseLibrary


REMOTE_URL = 'https://raw.githubusercontent.com/yuhonas/free-exercise-db/master/dist/exercises.json'
LOCAL_CLONE_PATH = Path('C:/Users/rajus/fitlife/free-exercise-db/dist/exercises.json')


def _slugify(name: str) -> str:
    slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
    return slug or 'exercise'


def _image_url(image_path: str) -> str:
    return f'https://raw.githubusercontent.com/yuhonas/free-exercise-db/master/exercises/{image_path}'


def load_dataset():
    if LOCAL_CLONE_PATH.exists():
        return json.loads(LOCAL_CLONE_PATH.read_text(encoding='utf-8'))
    response = requests.get(REMOTE_URL, timeout=60)
    response.raise_for_status()
    return response.json()


def main():
    app = create_app()
    with app.app_context():
        exercises = load_dataset()
        ExerciseLibrary.query.delete()
        db.session.commit()

        inserted = 0
        for item in exercises:
            images = [_image_url(path) for path in item.get('images', [])]
            db.session.add(ExerciseLibrary(
                external_id=item.get('id'),
                name=item.get('name'),
                slug=_slugify(item.get('name', 'exercise')),
                source='free-exercise-db',
                level=item.get('level'),
                category=item.get('category'),
                force=item.get('force'),
                mechanic=item.get('mechanic'),
                equipment=item.get('equipment'),
                primary_muscles=item.get('primaryMuscles', []),
                secondary_muscles=item.get('secondaryMuscles', []),
                instructions=item.get('instructions', []),
                image_urls=images,
                image_url=images[0] if images else None,
                demo_media_url=images[1] if len(images) > 1 else (images[0] if images else None),
                tags=list({*(item.get('primaryMuscles', []) or []), item.get('category') or ''})
            ))
            inserted += 1
            if inserted % 100 == 0:
                db.session.flush()

        db.session.commit()
        print(f'Imported {inserted} exercises into exercise_library.')


if __name__ == '__main__':
    main()
