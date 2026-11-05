# Course notes

Markdown notes shown at `/learn/courses/<course>/<year>`. Each folder here is a course, and each folder inside it is a year:

```
content/courses/
  python/
    2026/
      index.md        -> /learn/courses/python/2026
      workshop-1.md   -> /learn/courses/python/2026/workshop-1
      workshop-2.md   -> /learn/courses/python/2026/workshop-2
```

A new course or year needs no code changes: add the folder with an `index.md` and it appears at the matching URL. Link to it from `templates/courses.html`.

## Adding a session

1. Add a `.md` file to the year folder. The file name becomes the URL, so use lowercase letters, numbers and hyphens (`workshop-3.md`).
2. Start it with this frontmatter:

   ```yaml
   ---
   title: 'Workshop 3'
   course: 'Python Course'
   description: 'One line on what the session covers.'
   date: 2026-10-29
   order: 3
   authors: ['first-last', 'first-last']
   ---
   ```

   `title`, `course`, `description` and `date` are required. `order` sets the position in the sidebar and must be unique within the year. `authors` are written as `first-last` ids and shown as "First Last". Add `draft: true` to hide a file while you're still writing it.
3. Run `flask course-validate` before opening the PR. CI runs the same check.

A session only appears on the site once its `date` has passed, so a file can be merged before the session runs.

This is the same frontmatter Warwick AI's website uses, so files can be copied between the two repos without edits.

## Writing the notes

Standard markdown plus tables. Put answers in a collapsible block, leaving a blank line after `<summary>` so the markdown inside still renders:

```markdown
<details>
<summary>Answer</summary>

Markdown, tables and code blocks work here.

</details>
```

Fenced code blocks tagged with a language (` ```python `) are syntax highlighted.

## Credit

The Python Course 2026 notes are shared with Warwick AI, who wrote workshops 1 and 2. Their website code and content are released under the MIT License:

