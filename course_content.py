"""Markdown course notes for /learn/courses/<course>/<year>.

Each course year is a folder under content/courses/<course>/<year>/ holding
an index.md (the course overview) and one .md file per session. The files use
the same frontmatter as Warwick AI's website, so they can be copied between the
two repos without edits.

A session only appears on the site once its `date` has passed and it is not
marked `draft: true`.
"""

import datetime
import os
import re

import yaml
from markdown_it import MarkdownIt
from mdit_py_plugins.anchors import anchors_plugin
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
CONTENT_ROOT = os.path.join(REPO_ROOT, "content", "courses")
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)", re.DOTALL)

REQUIRED_FIELDS = {
    "title": str,
    "course": str,
    "description": str,
    "date": datetime.date,
}
OPTIONAL_FIELDS = {
    "order": int,
    "authors": list,
    "tags": list,
    "draft": bool,
    "image": str,
}


class CourseContentError(Exception):
    """Raised when a course file has missing or malformed frontmatter."""


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------

_code_formatter = HtmlFormatter(nowrap=True)


def _highlight_code(code, lang, _attrs):
    if not lang:
        return ""  # markdown-it escapes and wraps the code itself
    try:
        lexer = get_lexer_by_name(lang)
    except ClassNotFound:
        return ""
    return highlight(code, lexer, _code_formatter)


def _render_link_open(self, tokens, idx, options, env):
    token = tokens[idx]
    href = token.attrGet("href") or ""
    if href.startswith(("http://", "https://")):
        token.attrSet("target", "_blank")
        token.attrSet("rel", "noopener noreferrer")
    return self.renderToken(tokens, idx, options, env)


def _render_table_open(self, tokens, idx, options, env):
    return '<div class="table-wrap">' + self.renderToken(tokens, idx, options, env)


def _render_table_close(self, tokens, idx, options, env):
    return self.renderToken(tokens, idx, options, env) + "</div>"


def _build_markdown():
    # CommonMark is needed rather than Python-Markdown: the answers sit inside
    # <details> blocks and contain tables and code, which CommonMark renders
    # because of the blank line after <summary>.
    md = MarkdownIt("commonmark", {"html": True, "highlight": _highlight_code})
    md.enable("table")
    md.use(anchors_plugin, min_level=2, max_level=3)
    md.add_render_rule("link_open", _render_link_open)
    md.add_render_rule("table_open", _render_table_open)
    md.add_render_rule("table_close", _render_table_close)
    return md


_md = _build_markdown()


def _render(body):
    tokens = _md.parse(body)
    toc = []
    for i, token in enumerate(tokens):
        if token.type == "heading_open" and token.tag in ("h2", "h3"):
            toc.append(
                {
                    "id": token.attrGet("id"),
                    "text": tokens[i + 1].content,
                    "level": int(token.tag[1]),
                }
            )
    html = _md.renderer.render(tokens, _md.options, {})
    return html, toc


# ---------------------------------------------------------------------------
# Loading files
# ---------------------------------------------------------------------------

def _author_name(author_id):
    return " ".join(part.capitalize() for part in author_id.split("-"))


def _parse_frontmatter(path, text):
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise CourseContentError(f"{path}: missing frontmatter block between '---' lines")
    try:
        meta = yaml.safe_load(match.group(1)) or {}
    except (yaml.YAMLError, ValueError) as e:
        # ValueError covers impossible dates such as 2026-13-01
        raise CourseContentError(f"{path}: frontmatter could not be read ({e})")
    if not isinstance(meta, dict):
        raise CourseContentError(f"{path}: frontmatter must be a set of key: value pairs")

    if isinstance(meta.get("date"), datetime.datetime):
        meta["date"] = meta["date"].date()

    for field, kind in REQUIRED_FIELDS.items():
        if field not in meta:
            raise CourseContentError(f"{path}: missing required field '{field}'")
        if not isinstance(meta[field], kind):
            raise CourseContentError(
                f"{path}: '{field}' should be a {kind.__name__}"
                + (" in YYYY-MM-DD format" if kind is datetime.date else "")
            )
    for field, kind in OPTIONAL_FIELDS.items():
        if field in meta and not isinstance(meta[field], kind):
            raise CourseContentError(f"{path}: '{field}' should be a {kind.__name__}")
    for author in meta.get("authors", []):
        if not isinstance(author, str):
            raise CourseContentError(f"{path}: each entry in 'authors' should be text")

    return meta, text[match.end():]


_cache = {}


def _load_file(path, slug):
    mtime = os.path.getmtime(path)
    cached = _cache.get(path)
    if cached and cached[0] == mtime:
        return cached[1]

    with open(path, encoding="utf-8") as f:
        text = f.read()
    meta, body = _parse_frontmatter(_display_path(path), text)
    html, toc = _render(body)
    page = {
        "slug": slug,
        "title": meta["title"],
        "course": meta["course"],
        "description": meta["description"],
        "date": meta["date"],
        "order": meta.get("order", 0),
        "draft": meta.get("draft", False),
        "authors": [_author_name(a) for a in meta.get("authors", [])],
        "html": html,
        "toc": toc,
    }
    _cache[path] = (mtime, page)
    return page


def _display_path(path):
    return os.path.relpath(path, REPO_ROOT)


def _year_dir(course, year):
    if not SLUG_RE.match(course):
        return None
    path = os.path.join(CONTENT_ROOT, course, str(year))
    return path if os.path.isdir(path) else None


def load_course(course, year, today=None, include_unpublished=False):
    """Return the course overview and its sessions, or None if it doesn't exist.

    Sessions dated after `today` or marked as drafts are left out unless
    include_unpublished is set.
    """
    directory = _year_dir(course, year)
    if directory is None:
        return None
    index_path = os.path.join(directory, "index.md")
    if not os.path.isfile(index_path):
        return None

    today = today or datetime.date.today()
    overview = _load_file(index_path, "")
    if overview["draft"] and not include_unpublished:
        return None

    sessions = []
    for name in os.listdir(directory):
        if not name.endswith(".md") or name == "index.md":
            continue
        slug = name[:-3]
        if not SLUG_RE.match(slug):
            raise CourseContentError(
                f"{_display_path(os.path.join(directory, name))}: file names should be lowercase letters, numbers and hyphens"
            )
        page = _load_file(os.path.join(directory, name), slug)
        if include_unpublished or (not page["draft"] and page["date"] <= today):
            sessions.append(page)

    sessions.sort(key=lambda p: (p["order"], p["date"], p["slug"]))
    return {"course": course, "year": year, "overview": overview, "sessions": sessions}


def validate_all():
    """Load and render every course file. Returns a list of error messages."""
    errors = []
    if not os.path.isdir(CONTENT_ROOT):
        return errors
    for course in sorted(os.listdir(CONTENT_ROOT)):
        course_dir = os.path.join(CONTENT_ROOT, course)
        if not os.path.isdir(course_dir):
            continue
        for year in sorted(os.listdir(course_dir)):
            year_dir = os.path.join(course_dir, year)
            if not os.path.isdir(year_dir):
                continue
            if not year.isdigit():
                errors.append(f"{_display_path(year_dir)}: year folders should be named like 2026")
                continue
            if not os.path.isfile(os.path.join(year_dir, "index.md")):
                errors.append(f"{_display_path(year_dir)}: missing index.md")
                continue
            try:
                course_data = load_course(course, int(year), include_unpublished=True)
            except CourseContentError as e:
                errors.append(str(e))
                continue
            orders = {}
            for page in course_data["sessions"]:
                if page["order"] in orders:
                    errors.append(
                        f"{_display_path(year_dir)}: {page['slug']}.md and {orders[page['order']]}.md share order {page['order']}"
                    )
                orders[page["order"]] = page["slug"]
    return errors
