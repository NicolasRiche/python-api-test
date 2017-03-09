# Check if account parameters are valid
from validate_email import validate_email
import phonenumbers


def error_list(account):
    errors = []
    if (len(account.name) > 2 and len(account.name) <= 40) == False:
        errors.append({'name': 'Name length should be between 2 and 40 chars'})

    if validate_email(account.email) == False:
        errors.append({'email': 'Invalid email'})

    try:
        phone = phonenumbers.parse(account.phone_number, "CA")
        # TODO other than CA / US phone number
    except:
        errors.append({'phone_number': 'Invalid phone number'})

    # TODO address to .. country , need more checking than just str length
    if (len(account.address) > 0 and len(account.address) <= 400) == False:
        errors.append({'address': 'Address length should be between 1 and 400 chars'})

    if (len(account.city) > 0 and len(account.city) <= 50) == False:
        errors.append({'city': 'City length should be between 1 and 50 chars'})

    if (len(account.postal_code) > 0 and len(account.postal_code) <= 10) == False:
        errors.append({'postal_code': 'Postal code length should be between 1 and 10 chars'})

    if (len(account.country) > 0 and len(account.country) <= 30) == False:
        errors.append({'country': 'Country length should be between 1 and 30 chars'})

    return errors


def is_valid(account):
    error_list(account) == []
