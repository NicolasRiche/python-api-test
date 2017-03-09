import collections

AccountParams = collections.namedtuple('AccountParams', ['name', 'email', 'phone_number', 'address', 'city', 'postal_code', 'country'])

Account = collections.namedtuple('Account', ['id', 'name', 'email', 'phone_number', 'address', 'city', 'postal_code', 'country'])
