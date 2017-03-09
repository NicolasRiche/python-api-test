import unittest
import sqlite3
from account_api import sql_account_repository, entities

# Init context, create a temporary table in memory to run the tests
conn = sqlite3.connect(":memory:")
sql = sql_account_repository.SqlAccountRepository(conn)

test_base_accounts_params = entities.AccountParams(
    name="Nicolas", email="nicolas@domain.com", phone_number="611-611-6111",
    address="1 Main St", city="Ottawa", postal_code="K1S0A8", country="Canada"
)

expected_db_account = entities.Account(
    account_id=1, name="Nicolas", email="nicolas@domain.com", phone_number="611-611-6111",
    address="1 Main St", city="Ottawa", postal_code="K1S0A8", country="Canada"
)


class SqlTest(unittest.TestCase):
    def test_sql_sequence_use_case(self):
        print("-- Bad account parameters should throw error --")
        with self.assertRaisesRegex(ValueError, ".*Name.*"):
            bad_name_account = test_base_accounts_params._replace(name="")
            sql.add(bad_name_account)

        with self.assertRaisesRegex(ValueError, ".*email.*"):
            bad_email_account = test_base_accounts_params._replace(email="")
            sql.add(bad_email_account)

        with self.assertRaisesRegex(ValueError, ".*phone.*"):
            bad_phone_account = test_base_accounts_params._replace(phone_number="")
            sql.add(bad_phone_account)

            # TODO test more conditions

        #
        print("-- Valid account should succeed to be added --")
        valid_account_params = test_base_accounts_params  # We expect that sql repo return us a valid Account object (not AccountParams)
        self.assertEqual(sql.add(valid_account_params), expected_db_account)

        #
        print("-- Re-add an existing account should throw an error --")
        with self.assertRaisesRegex(ValueError, "An account with this name already exist in database"):
            already_exists_account_params = test_base_accounts_params
            sql.add(already_exists_account_params)

        # Even if we change the name, email has to be unique too
        with self.assertRaisesRegex(ValueError, "An account with this email already exist in database"):
            already_exists_account_params = test_base_accounts_params._replace(name="ChangedNicolas")
            sql.add(already_exists_account_params)

        #
        print("-- Find an existing id should succeed --")
        # At this moment we should still have only one entry in db with account_id == 1
        # We should be able to match it
        self.assertEqual(sql.find_by_id(1), expected_db_account)

        #
        print("-- Find a not-existing id should return None --")
        # At this moment we should still have only one entry in db with account_id == 1
        # We should be able to match it
        self.assertEqual(sql.find_by_id(2), None)

        #
        print("-- All accounts test 1 --")
        # If we list all accounts, we should have the one we added
        accounts = sql.all_accounts()
        self.assertEqual(accounts, [expected_db_account])

        #
        print("-- Add a second account (different than first) should succeed --")
        valid_account_params = test_base_accounts_params._replace(
            name="John", email="john@domain.com"
        )
        expected_db_account2 = expected_db_account._replace(
            account_id=2, name="John", email="john@domain.com"
        )
        self.assertEqual(sql.add(valid_account_params), expected_db_account2)

        #
        print("-- All accounts test 2 --")
        # If we list all accounts, we should have 2 accounts now
        accounts = sql.all_accounts()
        self.assertEqual(len(accounts), 2)


if __name__ == '__main__':
    unittest.main()
