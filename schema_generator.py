"""
Automatic JSON Schema Generator from SQLAlchemy Models
Generates JSON schemas from database models for data validation
"""
import json
from datetime import date
from sqlalchemy import String, Integer, Text, Date
from db_schema import db, ExecMember, BlogPost, Sponsor, SponsorNews


def sqlalchemy_to_json_type(column):
    """Convert SQLAlchemy column type to JSON schema type"""
    column_type = type(column.type)

    if column_type == String:
        return {"type": "string", "maxLength": column.type.length if column.type.length else 1000}
    elif column_type == Text:
        return {"type": "string"}
    elif column_type == Integer:
        return {"type": "integer"}
    elif column_type == Date:
        return {"type": "string", "format": "date"}
    else:
        # Default fallback
        return {"type": "string"}


def generate_model_schema(model_class):
    """Generate JSON schema for a SQLAlchemy model"""
    properties = {}
    required = []

    # Get table columns
    for column in model_class.__table__.columns:
        column_name = column.name

        # Get base type
        json_type = sqlalchemy_to_json_type(column)

        # Handle nullable fields
        if column.nullable:
            # Allow null values for nullable columns
            json_type = {"anyOf": [json_type, {"type": "null"}]}
        elif not column.primary_key:
            # Non-nullable, non-primary key fields are required
            required.append(column_name)

        # Handle default values and special cases
        if column.default is not None:
            if isinstance(json_type, dict) and "anyOf" in json_type:
                json_type["default"] = column.default.arg if hasattr(column.default, 'arg') else None
            else:
                json_type["default"] = column.default.arg if hasattr(column.default, 'arg') else None

        properties[column_name] = json_type

    schema = {
        "type": "object",
        "properties": properties,
        "required": required,
        "additionalProperties": False
    }

    return schema


def generate_all_schemas():
    """Generate schemas for all models"""
    models = {
        "exec_members": ExecMember,
        "blog_posts": BlogPost,
        "sponsors": Sponsor,
        "sponsor_news": SponsorNews
    }

    schemas = {}

    for name, model_class in models.items():
        schema = generate_model_schema(model_class)
        schemas[name] = {
            "title": f"{model_class.__name__} Schema",
            "description": f"JSON schema for {model_class.__tablename__} table",
            **schema
        }

    return schemas


def save_schemas_to_file(schemas, filepath="schemas.json"):
    """Save generated schemas to a JSON file"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(schemas, f, indent=2, ensure_ascii=False)
    print(f"✓ Schemas saved to {filepath}")


if __name__ == "__main__":
    print("Generating JSON schemas from SQLAlchemy models...")

    schemas = generate_all_schemas()
    save_schemas_to_file(schemas)

    # Print a summary
    for name, schema in schemas.items():
        print(f"  - {name}: {len(schema['properties'])} fields, {len(schema.get('required', []))} required")

    print("✅ Schema generation complete!")