# codesocWebsite

Warwick Codesoc website. Built using Flask. Originally owned by Warwick Coding Society's founder [Adriano Barbet](https://www.linkedin.com/in/adrianobarbet/) and contributed to by ex-Presidents [Piotr Zychlinksi](https://www.linkedin.com/in/piotr-zychlinski/) and [Alfie-Joe Smith](https://www.linkedin.com/in/alfiejfs/).

# Quickstart

- Changes to blog posts, exec members, sponsor news and sponsors can be made in the `data/` directory.
- Add events via the Warwick Coding Society GMail account in the Google Calendar.
  - Valid event prefixes include:
    - careers@
    - courses@
    - event@
    - social@
  - So for example, `event@ CodeSoc Pub Night`

## How to run

- First download the code from the repository
- Ensure both `clean.sh` and `setup.sh` have execute permissions, you can do this with `chmod u+x scriptname.sh`
- Run the `setup.sh` script to install required dependancies. _You must have python3 installed for this to work_
- Start the virtual environment by running `. venv/bin/activate`
- Install dependencies with `pip install -r requirements.txt`
- Define the file to run using `export FLASK_APP=codesoc.py`
- Build the database with `python -m flask db-reset`
- Run the development server with `python -m flask run`

You should now be able to view the website on the address specified by the server output, usually `127.0.0.1:5000`

## Development

Make sure your dependencies are installed:

```sh
./setup.sh
. venv/bin/activate
python -m pip install requirements.txt
```

You can validate data changes in the `data/` directory by using the flask command:

```sh
python -m flask db-validate
```

You can regenerate the SQLite database with:

```sh
python -m flask db-reset
```

### Database Migrations

When making changes to the database schema (models in `db_schema.py`):

1. **Create a migration** after modifying the models:
   ```sh
   export FLASK_APP=codesoc.py
   flask db migrate -m "Description of your changes"
   ```

2. **Apply the migration**:
   ```sh
   flask db upgrade
   ```

3. **Reset database with new schema**:
   ```sh
   flask db-reset
   ```

#### Troubleshooting Migrations

If you encounter migration conflicts or "table already exists" errors:

1. **Check current migration status**:
   ```sh
   flask db current
   ```

2. **If database is inconsistent, stamp it as current**:
   ```sh
   flask db stamp head
   ```

3. **Then create and apply your new migration**:
   ```sh
   flask db migrate -m "Your changes"
   flask db upgrade
   flask db-reset
   ```

The validation is ran per-PR and is required to merge. Build validation is also completed after.

#### Admin password notes

If you change the administrator password it may invalidate your session. Reset cookies if so otherwise this is an edge case.

#### Note to future devs

I really don't like this json-schema to database pipeline. Probably migrate to an external database instead of a local one and include backups. Also could just do JSON. Whatever is fine. 

Also we use PythonAnywhere as a hosting platform right now. Try to migrate somewhere free but this is again a pain. Flask is annoying, try to move to easier deployment models and so on. 

## C++ course hosting

The C++ course at `/learn/courses/cpp/` is a separate static site, built and deployed from the private [`uowcodingsociety/cpp-course`](https://github.com/uowcodingsociety/cpp-course) repository.
Flask does not serve it: a PythonAnywhere static file mapping does, and that mapping lives in the PythonAnywhere dashboard rather than in this repository.

- Web tab → Static files: URL `/learn/courses/cpp/` → Directory `/home/<PythonAnywhere user>/cpp-course-published/`.
- Requests for files that are not in that folder fall through to Flask, which returns 404.
- `codesoc.py` only redirects `/learn/courses/cpp` to `/learn/courses/cpp/`.
- This repository's deploy (`git reset --hard` in `~/website`) never touches the course folder.

Course releases are merges into the course repository's `prod` branch.
Course pages share this site's origin, so their JavaScript has the same power as this site's own pages, including a logged-in elections admin's session.
The organisation is on GitHub's Free plan, where the private course repository cannot require reviews: anyone with write access to it can deploy, and can read the deploy key through a workflow.
Keep that write access limited to people trusted like website admins, and review pull requests into its `prod` branch.

The course repository uploads with a dedicated SSH key whose line in `~/.ssh/authorized_keys` on PythonAnywhere is:

    command="/home/<PythonAnywhere user>/bin/rrsync -wo -munge /home/<PythonAnywhere user>/cpp-course-published",restrict ssh-ed25519 AAAA... cpp-course-deploy

`rrsync -wo` only lets the key write inside the course folder: no shell, no downloads, no paths outside it.
`-munge` breaks any uploaded symlinks, and `restrict` disables terminals and forwarding.

- Stop deploys: set the course repository's variable `CPP_COURSE_DEPLOY_ENABLED` to `false`.
- Hide the course: delete the static mapping and reload the web app.
- Revoke the key: delete its line from `~/.ssh/authorized_keys`.
- Rotate the key (yearly, whenever anyone with write access to the course repository leaves, or on any suspicion): generate a new ed25519 key, add its restricted line next to the old one, replace the course repository's `PYTHONANYWHERE_SSH_KEY` secret, confirm a deploy succeeds, then delete the old line.
