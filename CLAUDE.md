# Warwick Coding Society (CodeSoc)

The Warwick Coding Society is the coding hub at the University of Warwick, making learning code accessible to all students through free courses, workshops, mentorship, career support, and community events.

**Connect with us:**
- Instagram: @wwcodesoc
- Discord: https://discord.gg/NDCg2VwQxZ
- GitHub: Warwick-Coding-Society
- LinkedIn: Warwick Coding Society

# Development

## Setup
```sh
. venv/bin/activate
pip install -r requirements.txt
```

## Running
```sh
export FLASK_APP=codesoc.py
flask run
```

## Database Commands
- `flask db-validate` - Validate JSON data files against schemas
- `flask db-reset` - Reset database with validated JSON data
- `flask db-generate-schemas` - Generate JSON schemas from SQLAlchemy models

