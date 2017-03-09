import sqlite3
from . import account_validator, entities


class SqlAccountRepository:
    """Read / Write accounts on SQL database"""

    def __init__(self, sql_database):
        self.sql_database = sql_database
        # if table doesn't exist create it
        c = self.sql_database.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS "Accounts" (
        "account_id" INTEGER PRIMARY KEY NOT NULL UNIQUE , 
        "name" TEXT NOT NULL UNIQUE , "email" TEXT NOT NULL UNIQUE, 
        "phone_number" TEXT NOT NULL , 
        "address" TEXT NOT NULL , 
        "city" TEXT NOT NULL , 
        "postal_code" TEXT NOT NULL , 
        "country" TEXT NOT NULL 
        )''')
        self.sql_database.commit()

    def add(self, account_params):
        """ @type account AccountParams
        
        Add a new account
        
        If success return the inserted account, example
        Account(id=1, name='Nicolas', email='nicolas@domain.com', phone_number='611-611-6111', address='1 Main St', city='Ottawa', postal_code='K1S0A8', country='Canada')
            
        Else failure:
            ValueError : Name length should be between 2 and 40 chars
            ... other ValueError account parameters
            
            Is it possible too that add fail because the account already exists in database,
            both name & email have to be unique
            
            ValueError : An account with this name already exist in database
            ValueError : An account with this email already exist in database
        """
        param_errors = account_validator.error_list(account_params)
        if param_errors:
            raise ValueError(str(list(param_errors[0].values())[0]))  # raise the first param field error found

        if self.find_by_name(account_params.name) is not None:
            raise ValueError("An account with this name already exist in database")
        if self.find_by_email(account_params.email) is not None:
            raise ValueError("An account with this email already exist in database")

        # input values are valid & account doesn't exist yet, we can insert it in DB
        c = self.sql_database.cursor()
        try:
            c.execute("""INSERT INTO Accounts (name,email,phone_number,address,city,postal_code,country) 
                          VALUES (?,?,?,?,?,?,?)""",
                      (account_params.name, account_params.email, account_params.phone_number,
                       account_params.address, account_params.city, account_params.postal_code,
                       account_params.country)
                      )
        except sqlite3.IntegrityError as err:
            # Even if we check is account already exist before,
            # the insert query can fail if sql insert happened in parallel (by the python app or by another program).
            # As name&email have unique constraint, sql will throw an Integrity Error
            print("sqlite3.IntegrityError: {0}".format(err))
            raise
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise

        # print('sql result {0}'.format(r))
        self.sql_database.commit()
        inserted_id = c.lastrowid
        inserted_account = entities.Account._make([inserted_id] + list(account_params._asdict().values()))
        return inserted_account

    def find_by_id(self, id):
        """Return found Account or None"""
        c = self.sql_database.cursor()
        c.execute("SELECT * FROM Accounts WHERE account_id=?", [id])
        return self.__fetchone_account(c)

    def find_by_name(self, name):
        """Return found Account or None"""
        c = self.sql_database.cursor()
        c.execute("SELECT * FROM Accounts WHERE name=?", [name])
        return self.__fetchone_account(c)

    def find_by_email(self, email):
        """Return found Account or None"""
        c = self.sql_database.cursor()
        c.execute("SELECT * FROM Accounts WHERE email=?", [email])
        return self.__fetchone_account(c)

    def __fetchone_account(self, sql_cursor):
        fetch_result = sql_cursor.fetchone()
        if fetch_result is not None:
            found_account = entities.Account._make(fetch_result)
            return found_account
        else:
            return None
