# Install requirements
pip install -r requirements.txt

# How to start the flask app
./run.sh

# Run account repository tests
python3 -m unittest tests/sql_test.py
