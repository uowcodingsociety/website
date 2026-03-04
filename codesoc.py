from flask import Flask, render_template, request, jsonify, redirect, url_for, abort, session
from flask_migrate import Migrate
from db_schema import db, ExecMember, BlogPost, Sponsor, SponsorNews, ElectionCandidate, ElectionVote, ElectionSettings
from flask_mail import Mail, Message
import click
import os
import json
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
from db_manager import DatabaseManager
from schema_generator import generate_all_schemas, save_schemas_to_file
import csv
import requests
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError

# Load environment variables from .env file
# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(script_dir, ".env")
load_dotenv(dotenv_path=dotenv_path)

app = Flask(__name__)

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")
app.secret_key = ADMIN_PASSWORD

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME", "")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD", "")
app.config["AOC_SESSION_COOKIE"] = os.environ.get("AOC_SESSION_COOKIE", "")
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

# SU membership API configuration
SU_KEY = os.environ.get("SU_KEY", "")
SU_CACHE_DURATION = timedelta(hours=1)
su_cache = {"members": None, "last_updated": None}


def get_su_members():
    """Fetch and cache SU membership list. Returns dict of {student_id: full_name}."""
    now = datetime.now()
    if (
        su_cache["members"] is not None
        and su_cache["last_updated"] is not None
        and now - su_cache["last_updated"] < SU_CACHE_DURATION
    ):
        return su_cache["members"]

    url = f"https://www.warwicksu.com/membershipapi/listMembers/{SU_KEY}/"
    response = requests.get(url, timeout=15)
    response.raise_for_status()

    root = ET.fromstring(response.text)
    members = {}
    for member in root.findall("Member"):
        uid_el = member.find("UniqueID")
        first_el = member.find("FirstName")
        last_el = member.find("LastName")
        if uid_el is not None:
            uid = int(uid_el.text)
            first = (first_el.text or "").strip() if first_el is not None else ""
            last = (last_el.text or "").strip() if last_el is not None else ""
            members[uid] = f"{first} {last}".strip()

    su_cache["members"] = members
    su_cache["last_updated"] = now
    return members


def load_elections_json():
    """Load elections.json and return the categories list."""
    path = os.path.join(os.path.dirname(__file__), "data", "elections.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)["categories"]


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


# ── Elections ─────────────────────────────────────────────────────────────────

@app.context_processor
def inject_elections_status():
    try:
        settings = ElectionSettings.query.get(1)
        return {"elections_open": settings.isOpen if settings else False}
    except Exception:
        return {"elections_open": False}


@app.route("/elections")
def elections():
    settings = ElectionSettings.query.get(1)
    is_open = settings.isOpen if settings else False
    categories = load_elections_json()
    return render_template("elections.html", pageName="elections", is_open=is_open, categories=categories)


@app.route("/elections/administrator/login", methods=["GET", "POST"])
def elections_admin_login():
    error = None
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("elections_admin"))
        error = "Incorrect password."
    return render_template("elections-admin-login.html", error=error)


@app.route("/elections/administrator/logout")
def elections_admin_logout():
    session.pop("admin", None)
    return redirect(url_for("elections_admin_login"))


@app.route("/elections/administrator")
def elections_admin():
    if not session.get("admin"):
        return redirect(url_for("elections_admin_login"))
    settings = ElectionSettings.query.get(1)
    if not settings:
        settings = ElectionSettings()
        settings.id = 1
        db.session.add(settings)
        db.session.commit()
    return render_template("elections-admin.html", pageName="elections", is_open=settings.isOpen)


@app.route("/elections/<slug>")
def elections_category(slug):
    settings = ElectionSettings.query.get(1)
    if not settings or not settings.isOpen:
        return redirect(url_for("elections"))

    categories = load_elections_json()
    category = next((c for c in categories if c["slug"] == slug), None)
    if category is None:
        abort(404)

    position_order = [p["title"] for p in category["positions"]]
    candidates = ElectionCandidate.query.filter_by(categorySlug=slug).all()

    positions_dict = {title: [] for title in position_order}
    for c in candidates:
        if c.positionTitle in positions_dict:
            positions_dict[c.positionTitle].append(c)

    # Only include positions that have at least one candidate
    positions = [(title, positions_dict[title]) for title in position_order if positions_dict[title]]

    return render_template(
        "elections-category.html",
        pageName="elections",
        category=category,
        positions=positions,
    )


@app.route("/api/elections/settings", methods=["GET"])
def elections_settings_get():
    settings = ElectionSettings.query.get(1)
    return jsonify({"isOpen": settings.isOpen if settings else False})


@app.route("/api/elections/settings", methods=["POST"])
def elections_settings_post():
    data = request.get_json()
    settings = ElectionSettings.query.get(1)
    if not settings:
        settings = ElectionSettings()
        settings.id = 1
        db.session.add(settings)
    closing = settings.isOpen and not bool(data.get("isOpen", False))
    settings.isOpen = bool(data.get("isOpen", False))
    db.session.commit()

    if closing:
        _dump_votes_to_csv()

    return jsonify({"isOpen": settings.isOpen})


@app.route("/api/elections/verify", methods=["POST"])
def elections_verify():
    data = request.get_json()
    category_slug = data.get("category_slug")

    try:
        raw_id = str(data.get("student_id", "")).strip().lstrip("Uu")
        student_id = int(raw_id)
    except (ValueError, TypeError):
        return jsonify({"valid": False, "error": "Invalid student ID format"}), 400

    try:
        members = get_su_members()
    except Exception:
        return jsonify({"valid": False, "error": "Could not verify membership, please try again"}), 500

    if student_id not in members:
        return jsonify({"valid": False, "error": "Student ID not found in CodeSoc membership list"})

    already_voted = False
    if category_slug:
        already_voted = ElectionVote.query.filter_by(
            voterStudentID=student_id, categorySlug=category_slug
        ).first() is not None

    return jsonify({"valid": True, "name": members[student_id], "alreadyVoted": already_voted})


@app.route("/api/elections/vote", methods=["POST"])
def elections_vote():
    settings = ElectionSettings.query.get(1)
    if not settings or not settings.isOpen:
        return jsonify({"error": "Elections are currently closed"}), 403

    data = request.get_json()
    category_slug = data.get("category_slug")
    votes = data.get("votes", [])

    try:
        raw_id = str(data.get("student_id", "")).strip().lstrip("Uu")
        student_id = int(raw_id)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid student ID"}), 400

    if not category_slug:
        return jsonify({"error": "Missing category"}), 400

    # Re-verify membership server-side
    try:
        members = get_su_members()
    except Exception:
        return jsonify({"error": "Could not verify membership"}), 500

    if student_id not in members:
        return jsonify({"error": "Not a CodeSoc member"}), 403

    # Check already voted
    if ElectionVote.query.filter_by(voterStudentID=student_id, categorySlug=category_slug).first():
        return jsonify({"error": "Already voted in this category"}), 409

    POINTS = {1: 5, 2: 2, 3: 1}

    try:
        for v in votes:
            rank = v.get("rank")
            candidate_id = v.get("candidate_id")
            if rank not in POINTS or not candidate_id:
                continue
            candidate = ElectionCandidate.query.get(candidate_id)
            if not candidate or candidate.categorySlug != category_slug:
                return jsonify({"error": "Invalid candidate"}), 400
            db.session.add(ElectionVote(
                voterStudentID=student_id,
                candidateID=candidate_id,
                positionTitle=candidate.positionTitle,
                categorySlug=category_slug,
                rank=rank,
                points=POINTS[rank],
            ))
        db.session.commit()
        return jsonify({"success": True})
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Duplicate vote detected"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route("/api/elections/results")
def elections_results():
    categories = load_elections_json()
    results = []

    for category in categories:
        cat_data = {"name": category["name"], "slug": category["slug"], "positions": []}
        for position in category["positions"]:
            title = position["title"]
            candidates = ElectionCandidate.query.filter_by(
                categorySlug=category["slug"], positionTitle=title
            ).all()

            rows = []
            for c in candidates:
                r1 = ElectionVote.query.filter_by(candidateID=c.candidateID, rank=1).count()
                r2 = ElectionVote.query.filter_by(candidateID=c.candidateID, rank=2).count()
                r3 = ElectionVote.query.filter_by(candidateID=c.candidateID, rank=3).count()
                rows.append({
                    "name": c.name,
                    "points": r1 * 5 + r2 * 2 + r3,
                    "rank1": r1, "rank2": r2, "rank3": r3,
                })
            rows.sort(key=lambda x: x["points"], reverse=True)
            if rows:
                cat_data["positions"].append({"title": title, "candidates": rows})

        if cat_data["positions"]:
            results.append(cat_data)

    return jsonify(results)


@app.route("/api/elections/votes/reset/<slug>", methods=["POST"])
def elections_reset_slug_votes(slug):
    if not session.get("admin"):
        return jsonify({"error": "Unauthorised"}), 403

    filename, count = _dump_votes_to_csv(slug=slug)
    ElectionVote.query.filter_by(categorySlug=slug).delete()
    db.session.commit()

    return jsonify({"filename": filename, "count": count})


def _dump_votes_to_csv(slug=None):
    """Write votes to a timestamped CSV. Optionally filter by slug. Returns (filename, count)."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"votes_{slug}_{timestamp}.csv" if slug else f"votes_{timestamp}.csv"

    query = ElectionVote.query
    if slug:
        query = query.filter_by(categorySlug=slug)
    votes = query.order_by(
        ElectionVote.voterStudentID,
        ElectionVote.categorySlug,
        ElectionVote.positionTitle,
        ElectionVote.rank,
    ).all()

    candidates = {c.candidateID: c.name for c in ElectionCandidate.query.all()}

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "voter_student_id",
            "category_slug",
            "position_title",
            "rank",
            "points",
            "candidate_id",
            "candidate_name",
            "submitted_at",
        ])
        for v in votes:
            writer.writerow([
                v.voterStudentID,
                v.categorySlug,
                v.positionTitle,
                v.rank,
                v.points,
                v.candidateID,
                candidates.get(v.candidateID, "Unknown"),
                v.submittedAt.isoformat() if v.submittedAt else "",
            ])

    return filename, len(votes)


# CLI Commands for database management
@app.cli.command("db-dump-votes")
def db_dump_votes():
    """Dump all election votes to a timestamped CSV file."""
    filename, count = _dump_votes_to_csv()
    if count == 0:
        click.echo("⚠ No votes to dump.")
    else:
        click.echo(f"✅ Dumped {count} votes to {filename}")


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
