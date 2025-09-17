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

The validation is ran per-PR and is required to merge. Build validation is also completed after.
