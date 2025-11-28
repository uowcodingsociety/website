from flask import Flask, render_template, request, jsonify
from flask_migrate import Migrate
from db_schema import db, ExecMember, BlogPost, Sponsor, SponsorNews
from flask_mail import Mail, Message
import click
import os
from dotenv import load_dotenv
from db_manager import DatabaseManager
from schema_generator import generate_all_schemas, save_schemas_to_file
import requests
from datetime import datetime, timedelta

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME", "")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD", "")
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True

import os

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"sqlite:///{os.path.join(app.instance_path, 'codesoc.sqlite')}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
migrate = Migrate(app, db)
mail = Mail(app)

# Initialize database manager
db_manager = DatabaseManager()
db_manager.init_app(app)

# Advent of Code configuration
AOC_SESSION_COOKIE = os.environ.get("AOC_SESSION_COOKIE", "")
AOC_LEADERBOARD_ID = "3615951"
AOC_YEAR = "2025"
AOC_CACHE_DURATION = timedelta(minutes=15)

# Cache for leaderboard data
aoc_cache = {"data": None, "last_updated": None}


@app.route("/")
def home():
    return render_template("Home.html", pageName="home")


@app.route("/learn")
def learn():
    return render_template("learn.html", pageName="learn")


@app.route("/learn/courses", methods=["GET", "POST"])
def courses():
    if request.method == "POST":
        courseOption = request.form.get("courseOption")
        courseFeedback = request.form.get("message")
        msg = Message(
            "Course feedback: " + courseOption,
            sender=("Course Feedback Bot", app.config["MAIL_USERNAME"]),
            recipients=["info@warwickcodingsociety.com"],
        )
        msg.html = (
            "<h1><b>"
            + courseOption
            + "</b> Course Feedback:</h1> <p>"
            + courseFeedback
            + "</p>"
        )
        msg.body = courseOption + " Course Feedback: " + courseFeedback
        mail.send(msg)
    return render_template("courses.html", pageName="courses")


@app.route("/learn/mentorship")
def mentorship():
    return render_template("mentorship.html", pageName="mentorship")


@app.route("/woco")
def woco():
    return render_template("woco.html", pageName="woco")


@app.route("/careers")
def careers():
    return render_template("careers.html", pageName="careers")


@app.route("/careers/sponsors")
def sponsors():
    sponsors = Sponsor.query.all()
    sponsorNews = SponsorNews.query.order_by(SponsorNews.newsDate.desc()).all()
    sponsorNewsSponsorList = []
    for news in sponsorNews:
        newsDict = {"news": news, "sponsor": Sponsor.query.get(news.sponsorID)}
        sponsorNewsSponsorList.append(newsDict)
    return render_template(
        "sponsors.html",
        pageName="sponsors",
        sponsors=sponsors,
        sponsorNews=sponsorNewsSponsorList,
    )


@app.route("/develop")
def develop():
    return render_template("develop.html", pageName="develop")


@app.route("/events")
def events():
    return render_template("events.html", pageName="events")


@app.route("/exec-team")
def execTeam():
    execMembers = ExecMember.query.all()
    return render_template(
        "exec-team.html", pageName="execTeam", execMembers=execMembers
    )


@app.route("/aoc")
def aoc():
    return render_template("aoc.html", pageName="aoc")


@app.route("/blog")
def blog():
    blogPosts = BlogPost.query.all()
    latestBlogPost = blogPosts[0]
    for blogPost in blogPosts:
        if blogPost.postCreationDate > latestBlogPost.postCreationDate:
            latestBlogPost = blogPost
    blogPosts.remove(latestBlogPost)

    return render_template(
        "blog.html", pageName="blog", latestBlogPost=latestBlogPost, blogPosts=blogPosts
    )


@app.route("/blog/<blogID>")
def payBill(blogID):
    blog = BlogPost.query.get(blogID)
    if blog != None:
        return render_template("blogPost.html", blogPost=blog, pageName="blog")
    else:
        return render_template("blogNotFound.html", pageName="blog")


@app.route("/api/aoc/leaderboard")
def aoc_leaderboard():
    """Fetch Advent of Code leaderboard data with 15-minute caching"""
    if not AOC_SESSION_COOKIE:
        return jsonify({"error": "AOC session cookie not configured"}), 500

    # Check if we have valid cached data
    now = datetime.now()
    if (
        aoc_cache["data"] is not None
        and aoc_cache["last_updated"] is not None
        and now - aoc_cache["last_updated"] < AOC_CACHE_DURATION
    ):
        response_data = aoc_cache["data"].copy()
        response_data["cached_at"] = aoc_cache["last_updated"].isoformat()
        return jsonify(response_data)

    # Cache is expired or empty, fetch new data
    try:
        url = f"https://adventofcode.com/{AOC_YEAR}/leaderboard/private/view/{AOC_LEADERBOARD_ID}.json"
        cookies = {"session": AOC_SESSION_COOKIE}
        response = requests.get(url, cookies=cookies, timeout=10)
        response.raise_for_status()

        # Update cache
        aoc_cache["data"] = response.json()
        aoc_cache["last_updated"] = now

        response_data = aoc_cache["data"].copy()
        response_data["cached_at"] = now.isoformat()
        return jsonify(response_data)
    except requests.exceptions.RequestException as e:
        # If API call fails but we have stale cached data, return it anyway
        if aoc_cache["data"] is not None:
            response_data = aoc_cache["data"].copy()
            if aoc_cache["last_updated"] is not None:
                response_data["cached_at"] = aoc_cache["last_updated"].isoformat()
            return jsonify(response_data)
        return jsonify({"error": str(e)}), 500


# CLI Commands for database management
@app.cli.command("db-reset")
def db_reset():
    """Reset database with validated JSON data"""
    click.echo("🔄 Resetting database...")

    with app.app_context():
        success = db_manager.reset_database()
        if success:
            click.echo("🎉 Database reset completed successfully!")
        else:
            click.echo("❌ Database reset failed!")


@app.cli.command("db-validate")
def db_validate():
    """Validate JSON data files against schemas"""
    click.echo("🔍 Validating JSON data files...")

    with app.app_context():
        db_manager.generate_and_load_schemas()
        is_valid, _ = db_manager.validate_all_data_files()

        if is_valid:
            click.echo("✅ All JSON files are valid!")
        else:
            click.echo("❌ Validation errors found!")


@app.cli.command("db-generate-schemas")
def db_generate_schemas():
    """Generate JSON schemas from SQLAlchemy models"""
    click.echo("🔄 Generating JSON schemas...")

    schemas = generate_all_schemas()
    save_schemas_to_file(schemas)

    click.echo("✅ Schemas generated and saved to schemas.json")
    for name, schema in schemas.items():
        click.echo(f"  - {name}: {len(schema['properties'])} fields")


if __name__ == "__main__":
    app.run(debug=True)
