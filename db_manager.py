"""
Database Manager with JSON Schema Validation
Handles database regeneration with validated JSON data
"""
import json
import os
from datetime import datetime
from flask import Flask
from jsonschema import validate, ValidationError
from db_schema import db, ExecMember, BlogPost, Sponsor, SponsorNews
from schema_generator import generate_all_schemas


class DatabaseManager:
    def __init__(self, app=None):
        self.app = app
        self.schemas = {}

    def init_app(self, app):
        """Initialize with Flask app"""
        self.app = app

    def generate_and_load_schemas(self):
        """Generate schemas from models and load them"""
        print("🔄 Generating schemas from SQLAlchemy models...")
        self.schemas = generate_all_schemas()
        print("✓ Schemas generated and loaded")
        return self.schemas

    def validate_json_file(self, file_path, schema_name):
        """Validate a single JSON file against its schema"""
        if schema_name not in self.schemas:
            raise ValueError(f"Schema '{schema_name}' not found")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Validate each item in the array
            schema = self.schemas[schema_name]
            errors = []

            for i, item in enumerate(data):
                try:
                    validate(item, schema)
                except ValidationError as e:
                    errors.append(f"Item {i+1}: {e.message}")

            if errors:
                print(f"❌ Validation errors in {file_path}:")
                for error in errors:
                    print(f"  - {error}")
                return False, errors

            print(f"✓ {file_path} validated ({len(data)} items)")
            return True, data

        except FileNotFoundError:
            print(f"❌ File not found: {file_path}")
            return False, [f"File not found: {file_path}"]
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in {file_path}: {e}")
            return False, [f"Invalid JSON: {e}"]

    def validate_all_data_files(self):
        """Validate all JSON data files"""
        files_to_validate = [
            ("data/exec_members.json", "exec_members"),
            ("data/blog_posts.json", "blog_posts"),
            ("data/sponsors.json", "sponsors"),
            ("data/sponsor_news.json", "sponsor_news")
        ]

        all_valid = True
        validated_data = {}

        print("🔍 Validating JSON data files...")

        for file_path, schema_name in files_to_validate:
            is_valid, result = self.validate_json_file(file_path, schema_name)
            if is_valid:
                validated_data[schema_name] = result
            else:
                all_valid = False

        if all_valid:
            print("✅ All JSON files validated successfully")
        else:
            print("❌ Validation failed for one or more files")

        return all_valid, validated_data

    def clear_database(self):
        """Clear all data from database tables"""
        print("🗑️  Clearing existing database data...")

        # Ensure instance directory exists and create tables
        import os
        os.makedirs(self.app.instance_path, exist_ok=True)
        db.create_all()

        # Delete in reverse order of dependencies
        db.session.query(SponsorNews).delete()
        db.session.query(Sponsor).delete()
        db.session.query(BlogPost).delete()
        db.session.query(ExecMember).delete()

        db.session.commit()
        print("✓ Database cleared")

    def load_data_to_database(self, validated_data):
        """Load validated data into database"""
        print("📥 Loading data into database...")

        # Load ExecMembers
        if "exec_members" in validated_data:
            for item in validated_data["exec_members"]:
                member = ExecMember(
                    name=item.get('name'),
                    course=item.get('course'),
                    bio=item.get('bio'),
                    nationality=item.get('nationality'),
                    pronouns=item.get('pronouns'),
                    team=item.get('team'),
                    title=item.get('title'),
                    liLink=item.get('liLink', ''),
                    year=item.get('year', ''),
                    ghLink=item.get('ghLink', '')
                )
                member.execID = item['execID']
                if item.get('name'):
                    member.imageLink = item['name'].replace(' ', '')
                db.session.add(member)
            print(f"  ✓ Added {len(validated_data['exec_members'])} exec members")

        # Load BlogPosts
        if "blog_posts" in validated_data:
            for item in validated_data["blog_posts"]:
                post = BlogPost(
                    postTitle=item['postTitle'],
                    postDescription=item['postDescription'],
                    postTags=item['postTags'],
                    postContent=item['postContent'],
                    postAuthor=item['postAuthor'],
                    postImageURL=item['postImageURL']
                )
                post.postID = item['postID']
                # Parse date
                post.postCreationDate = datetime.strptime(item['postCreationDate'], '%Y-%m-%d').date()
                db.session.add(post)
            print(f"  ✓ Added {len(validated_data['blog_posts'])} blog posts")

        # Load Sponsors
        if "sponsors" in validated_data:
            for item in validated_data["sponsors"]:
                sponsor = Sponsor(
                    sponsorName=item['sponsorName'],
                    sponsorDescription=item['sponsorDescription'],
                    sponsorIndustry=item['sponsorIndustry'],
                    sponsorTier=item['sponsorTier'],
                    sponsorSiteURL=item['sponsorSiteURL'],
                    sponsorImageName=item['sponsorImageName']
                )
                sponsor.sponsorID = item['sponsorID']
                db.session.add(sponsor)
            print(f"  ✓ Added {len(validated_data['sponsors'])} sponsors")

        # Load SponsorNews
        if "sponsor_news" in validated_data:
            for item in validated_data["sponsor_news"]:
                news = SponsorNews(
                    sponsorID=item['sponsorID'],
                    newsTitle=item['newsTitle'],
                    newsDescription=item['newsDescription'],
                    newsURL=item['newsURL'],
                    newsImageName=item['newsImageName']
                )
                news.newsID = item['newsID']
                db.session.add(news)
            print(f"  ✓ Added {len(validated_data['sponsor_news'])} sponsor news items")

        db.session.commit()
        print("✅ All data loaded successfully")

    def reset_database(self):
        """Complete database reset with validation"""
        print("🔄 Starting database reset...")

        # Generate fresh schemas
        self.generate_and_load_schemas()

        # Validate all data
        is_valid, validated_data = self.validate_all_data_files()
        if not is_valid:
            print("❌ Database reset aborted due to validation errors")
            return False

        # Clear and reload database
        with self.app.app_context():
            self.clear_database()
            self.load_data_to_database(validated_data)

        print("🎉 Database reset completed successfully!")
        return True


def create_app():
    """Create Flask app for standalone usage"""
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(app.instance_path, 'codesoc.sqlite')}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        os.makedirs(app.instance_path, exist_ok=True)
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    manager = DatabaseManager(app)

    with app.app_context():
        manager.reset_database()