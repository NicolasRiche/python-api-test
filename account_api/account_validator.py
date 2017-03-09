# Check if account parameters are valid
from validate_email import validate_email
import phonenumbers


def error_list(account_params):
    """ @type AccountParams
    Check accounts parameters (name, email, ...) for example at sign-up
    Return an error list"""
    errors = []
    if not (len(account_params.name) > 2 and len(account_params.name) <= 40):
        errors.append({'name': 'Name length should be between 2 and 40 chars'})

    if not validate_email(account_params.email):
        errors.append({'email': 'Invalid email'})

    try:
        phone = phonenumbers.parse(account_params.phone_number, "CA")
        # TODO other than CA / US phone number
    except:
        errors.append({'phone_number': 'Invalid phone number'})

    # TODO address to .. country , need more checking than just str length
    if not (len(account_params.address) > 0 and len(account_params.address) <= 400):
        errors.append({'address': 'Address length should be between 1 and 400 chars'})

    if not (len(account_params.city) > 0 and len(account_params.city) <= 50):
        errors.append({'city': 'City length should be between 1 and 50 chars'})

    if not (len(account_params.postal_code) > 0 and len(account_params.postal_code) <= 10):
        errors.append({'postal_code': 'Postal code length should be between 1 and 10 chars'})

    if not (len(account_params.country) > 0 and len(account_params.country) <= 30):
        errors.append({'country': 'Country length should be between 1 and 30 chars'})

    return errors


def is_valid(account_params):
    """ @type AccountParams
    Check accounts parameters (name, email, ...) for example at sign-up
    Return True if all parameters are valid"""
    error_list(account_params) == []
