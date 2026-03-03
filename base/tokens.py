from django.contrib.auth.tokens import PasswordResetTokenGenerator
import random
import string

class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        # Use str() instead of six.text_type
        return (
            str(user.pk) + str(timestamp) + 
            str(user.email_verified)
        )

email_verification_token = EmailVerificationTokenGenerator()

def generate_verification_code():
    """Generate a 6-digit verification code"""
    return ''.join(random.choices(string.digits, k=6))