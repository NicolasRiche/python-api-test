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


class SqlTest(unittest.TestCase):
    def test_cannot_add_invalid_account(self):
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

    def test_can_add_valid_account(self):
        valid_account_params = test_base_accounts_params
        self.assertEqual(sql.add(valid_account_params),
                         # We expect that sql repo return us a valid Account object (not AccountParams)
                         entities.Account(
                             id=1, name="Nicolas", email="nicolas@domain.com", phone_number="611-611-6111",
                             address="1 Main St", city="Ottawa", postal_code="K1S0A8", country="Canada"
                         )
                         )

    def test_cannot_add_existing_account(self):
        with self.assertRaisesRegex(ValueError, "An account with this name already exist in database"):
            already_exists_account_params = test_base_accounts_params
            sql.add(already_exists_account_params)

        # Even if we change the name, email has to be unique too
        with self.assertRaisesRegex(ValueError, "An account with this email already exist in database"):
            already_exists_account_params = test_base_accounts_params._replace(name="ChangedNicolas")
            sql.add(already_exists_account_params)


if __name__ == '__main__':
    unittest.main()
