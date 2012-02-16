from datetime import date
from django.utils.http import int_to_base36, base36_to_int
from django.utils.crypto import constant_time_compare, salted_hmac

class ExpiringTokenGenerator(object):
    # TODO: docstring
    key_salt = "toolbox.tokens.ExpiringTokenGenerator"
    timeout_days = 5
    
    def value_tuple(self, *args):
        """Return a tuple of values that will be used in creating the hash.
        Child classes probably want to replace this method with something more relevant to theire use-case.
        
        One should use values that will change when the hash is used
        (for example, a user's last_login timestamp or hashed password for a
        password-reset hash) so that the hash can only be used once."""
        return args
    
    def make_token(self, *args):
        """Return a token that expires after self.timeout_days and that can be
        used only once (provided that value_tuple() uses the right values)."""
        current_timestamp = self.make_timestamp(self._today())
        return self._make_token_with_timestamp(current_timestamp, *args)
    
    def make_timestamp(self, dt):
        """Return the number of days between the given datetime and Jan 1st 2001."""
        return (dt - date(2001, 1, 1)).days
    
    def check_token(self, token, *args):
        try:
            timestamp, hash = self.parse_token(token)
        except ValueError:
            return False
        
        # Check that the message/hash has not been tampered with
        correct_token = self._make_token_with_timestamp(timestamp, *args)
        if not constant_time_compare(correct_token, token):
            return False
        
        # Check the timestamp is within limit
        current_timestamp = self.make_timestamp(self._today())
        if (current_timestamp - timestamp) > self.timeout_days:
            return False
        
        return True
    
    def do_hash(self, value):
        # We limit the hash to 20 chars to keep URL short
        return salted_hmac(self.key_salt, value).hexdigest()[::2]
    
    def format_hash(self, timestamp, hash):
        """Merge the timestamp and the hash into a string."""
        ts_b36 = int_to_base36(timestamp)
        
        return '%s-%s' % (ts_b36, hash)
    
    def parse_token(self, token):
        """The inverse of format_hash()."""
        ts_b36, hash = token.split('-')
        return base36_to_int(ts_b36), hash
    
    def _make_token_with_timestamp(self, timestamp, *args):
        t = self.value_tuple(*args) + (timestamp,)
        value = ''.join(unicode(x) for x in t)
        hash = self.do_hash(value)
        return self.format_hash(timestamp, hash)
    
    def _today(self):
        # Used for mocking in tests
        return date.today()
