# Install requirements
pip install -r requirements.txt

# How to start the flask app
./run.sh

# Run account repository tests
python3 -m unittest tests/sql_test.py

# API doc
API doc in /static/apidoc/index.html
( served by flask at domain:port/static/apidoc/index.html or local html file can be directly in browser )