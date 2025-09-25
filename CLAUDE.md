# Warwick Coding Society (CodeSoc)

The Warwick Coding Society is the coding hub at the University of Warwick, making learning code accessible to all students through free courses, workshops, mentorship, career support, and community events.

**Connect with us:**

- Instagram: @wwcodesoc
- Discord: https://discord.gg/NDCg2VwQxZ
- GitHub: uowcodingsociety
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

## Database Migrations

When modifying database models in `db_schema.py`:

1. **Create migration**:

   ```sh
   flask db migrate -m "Description of changes"
   ```

2. **Apply migration**:

   ```sh
   flask db upgrade
   ```

3. **Reset with new schema**:
   ```sh
   flask db-reset
   ```

### Migration Troubleshooting

If you encounter "table already exists" or migration conflicts:

1. **Check migration status**: `flask db current`
2. **Stamp database as current**: `flask db stamp head`
3. **Create and apply new migration**:
   ```sh
   flask db migrate -m "Your changes"
   flask db upgrade
   flask db-reset
   ```

This ensures database schema and migration tracking stay synchronized.
