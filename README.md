# codesocWebsite
Warwick Codesoc website. Built using Flask.

## How to run
- First download the code from the repository
- Ensure both ```clean.sh``` and ```setup.sh``` have execute permissions, you can do this with ```chmod u+x scriptname.sh``` 
- Run the  ```setup.sh``` script to install required dependancies. *You must have python3 installed for this to work*
- Start the virtual environment by running ```. venv/bin/activate```
- Define the file to run using ```export FLASK_APP=codesoc.py```
- Run the development server with ```flask run```

You should now be able to view the website on the address specified by the server output, usually ```127.0.0.1:5000```


**ENSURE YOU RUN ```clean.sh``` BEFORE COMMITTING TO PREVENT UNNECESSARY FILES FROM BEING UPLOADED TO THE REPO**
