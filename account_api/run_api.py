from flask import Flask, jsonify, request, abort
import flask
import sqlite3
import sys
from account_api import sql_account_repository, entities, account_validator

app = Flask(__name__)

conn = sqlite3.connect("db.sqlite")
accounts_repo = sql_account_repository.SqlAccountRepository(conn)

# When we call jsonify, keep json keys order as in python code
app.config["JSON_SORT_KEYS"] = False


@app.route('/', methods=['GET'])
def home():
    return """REST API <a href="/static/apidoc/index.html">API doc /static/apidoc/index.html</a>"""

@app.route('/accounts/<int:id>', methods=['GET'])
def get_account(id):
    """GET /accounts/:id
    
    Get a single account by its id
    
    Return: 
      Success 
        Ok 200 Json { ... account json object ... }
      
      Failure 
        NotFound 404 "Account id:$id doesn't exist"
    
    """
    maybe_account = accounts_repo.find_by_id(id)
    if maybe_account is not None:
        return jsonify(maybe_account._asdict())
    else:
        abort(flask.make_response("Account id:{0} doesn't exist".format(id), 404))


@app.route('/accounts', methods=['GET'])
def all_accounts():
    """GET /accounts
    
    Return: 
      Success 
        Ok 200 Json [ ... list of accounts object ... ]
        example [ { account1 }, { account2 } ] , if no result [ ]
    
    """
    accounts = accounts_repo.all_accounts()
    accounts_dict = [acc._asdict() for acc in accounts]
    return jsonify(accounts_dict)


@app.route('/accounts/find_by_name', methods=['GET'])
def find_by_name():
    """GET /accounts/find_by_name?name=:name
    
    Find a account by its name (strict, name should match exactly)
    
    Params:
      - [required] 'name' : the name you look for

    Return:
      Success 
        Ok 200 Json [ {... account object ...} ] or [ ] if not found
        
      Failure
        - BadRequest 400 "Missing required 'name' url parameter"
        - BadRequest 400 "'name' url parameter cannot be empty"
    
    """
    name_query = request.args.get('name')
    if name_query is None:
        return "Missing required 'name' url parameter", 400
    if name_query.strip() == "":
        return "'name' url parameter cannot be empty", 400

    maybe_account = accounts_repo.find_by_name(name_query.strip())

    if maybe_account is not None:
        accounts = [maybe_account]
    else:
        accounts = []
    accounts_dict = [acc._asdict() for acc in accounts]
    return jsonify(accounts_dict)


@app.route('/accounts/find_by_email', methods=['GET'])
def find_by_email():
    """GET /accounts/find_by_email?email=:email
    
    Find a account by its email (strict, email should match exactly)
    
    Params:
      - [required] 'email' : the email you look for

    Return:
      Success 
        Ok 200 Json [ {... account object ...} ] or [ ] if not found
        
      Failure
        - BadRequest 400 "Missing required 'email' url parameter"
        - BadRequest 400 "'email' url parameter cannot be empty"
    
    """
    email_query = request.args.get('email')
    if email_query is None:
        return "Missing required 'email' url parameter", 400
    if email_query.strip() == "":
        return "'email' url parameter cannot be empty", 400

    maybe_account = accounts_repo.find_by_email(email_query.strip().lower())

    if maybe_account is not None:
        accounts = [maybe_account]
    else:
        accounts = []
    accounts_dict = [acc._asdict() for acc in accounts]
    return jsonify(accounts_dict)


@app.route('/accounts/create', methods=['POST'])
def create_account():
    """POST /accounts/create
    
    Require Json input ( "content-type": "application/json" and Json in the HTTP body )
    Example
    {
      "name": "NicolasLast", 
      "email": "nicolas@domain.com", 
      "phone_number": "611-611-6111", 
      "address": "1 Main St", 
      "city": "Ottawa", 
      "postal_code": "K1S0A8", 
      "country": "Canada"
    }
    
    Each field has some requirements (example name cannot be empty, email should be valid, etc)
    You can call POST /account/create_check_parameters to check values and get eventual error(s) to fix
    (For example to highlight error in create account form)
    
    Return:
     Success 
       Ok 200 Json { ... created account obj ... }
       
     Failure
       - BadRequest 400 "Expects a request content-type application/json"
       - BadRequest 400 "Missing required '$key' field in json"  # with key can be name, email, ...
       - BadRequest 400 "An account with this name already exist in database"
       - BadRequest 400 "An account with this email already exist in database"
       
    Call example with curl : 
    
    curl -i -X POST -H "Content-type: application/json" --data '{"name": "NicolasLast", 
    "email": "nicolas@domain.com", "phone_number": "611-611-6111", "address": "1 Main St", 
    "city": "Ottawa", "postal_code": "K1S0A8", "country": "Canada" }' "localhost:5000/accounts/create"

    """
    in_json = request.get_json()

    __check_account_params_fields_present(in_json)
    account_params = __dict_to_account_param(in_json)

    # We have all the fields in json , let's try to create an account
    # It can still fails if the value aren't valid, or account already exists.
    try:
        created_account = accounts_repo.add(account_params)
    except ValueError as err:
        # accounts_repo returns a ValueError when input isn't valid
        # So we return bad request to return the error message directly to API consumer
        abort(flask.make_response(flask.make_response(str(err)), 400))
    except:
        raise # if other than ValueError exception, something bad happened, we let flask generate a 500 error

    # Success, return the created account
    return jsonify(created_account._asdict())


@app.route('/accounts/create_check_parameters', methods=['POST'])
def create_check_parameters():
    """POST /accounts/create_check_parameters
    
    Require Json input ( "content-type": "application/json" and Json in the HTTP body )
    Example
    {
      "name": "NicolasLast", 
      "email": "nicolas@domain.com", 
      "phone_number": "611-611-6111", 
      "address": "1 Main St", 
      "city": "Ottawa", 
      "postal_code": "K1S0A8", 
      "country": "Canada"
    }
    
    Each field has some requirements (example name cannot be empty, email should be valid, etc)
    You can this endpoint to check values and get eventual error(s) to fix
    (For example to highlight error in create account form)
    
    Return:
     Success 
        Ok 200 Json 
        # return a list of errors formatted as
        [
         { "field1" : "error message1" },
         { "field2" : "error message2" },
         ...
        ]
       
        Example 
        [
           {
              "name":"An account with this name already exist in database"
           },
           {
              "email":"An account with this email already exist in database"
           },
           {
              "phone":"Invalid phone number"
           },
           {
              "city":"City length should be between 1 and 50 chars"
           }
        ]

       
     Failure
       - BadRequest 400 "Expects a request content-type application/json"
       - BadRequest 400 "Missing required '$key' field in json"  # with key can be name, email, ...
       
    Call example with curl : 
    
    curl -i -X POST -H "Content-type: application/json" --data '{"name": "NicolasLast", 
    "email": "nicolas@domain.com", "phone_number": "611-611-6111", "address": "1 Main St", 
    "city": "Ottawa", "postal_code": "K1S0A8", "country": "Canada" }' "localhost:5000/accounts/create_check_parameters"

    """
    in_json = request.get_json()

    __check_account_params_fields_present(in_json)

    account_params = __dict_to_account_param(in_json)

    param_errors = account_validator.error_list(account_params)
    if accounts_repo.find_by_name(account_params.name) is not None:
        param_errors.append({"name" : "An account with this name already exist in database"})
    if accounts_repo.find_by_email(account_params.email) is not None:
        param_errors.append({"email" : "An account with this email already exist in database"})

    if param_errors :
        return jsonify(param_errors)


def __check_account_params_fields_present(in_json):
    def check_field_present(field):
        if not ("name" in in_json):
            abort(flask.make_response("Missing required 'name' field in json", 400))
    check_field_present("name")
    check_field_present("email")
    check_field_present("phone_number")
    check_field_present("address")
    check_field_present("city")
    check_field_present("postal_code")
    check_field_present("country")

def __dict_to_account_param(in_dict):
    return entities.AccountParams(
        in_dict["name"].strip(),
        in_dict["email"].strip().lower(),
        in_dict["phone_number"].strip(),
        in_dict["address"].strip(),
        in_dict["city"].strip(),
        in_dict["postal_code"].strip().upper(),
        in_dict["country"].strip()
    )