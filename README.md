# codesocWebsite
Warwick Codesoc website. Built using Flask.

## How to run
- First download the code from the repository
- Ensure both ```clean.sh``` and ```setup.sh``` have execute permissions, you can do this with ```chmod u+x scriptname.sh``` 
- Run the  ```setup.sh``` script to install required dependancies. *You must have python3 installed for this to work*
- Start the virtual environment by running ```. venv/bin/activate```
- Install dependencies with `pip install -r requirements.txt`
- Define the file to run using ```export FLASK_APP=codesoc.py```
- Build the database with `python -m flask db-reset`
- Run the development server with ```python -m flask run```

You should now be able to view the website on the address specified by the server output, usually ```127.0.0.1:5000```

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

