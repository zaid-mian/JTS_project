import quopri
from django.core.mail.backends.console import EmailBackend as ConsoleEmailBackend

class DevelopmentEmailBackend(ConsoleEmailBackend):
    """
    Custom email backend for local development.
    Decodes quoted-printable transfer encoding in console outputs to display
    long URLs (like password reset links) as single, uninterrupted copyable lines.
    """
    def write_message(self, message):
        msg = message.message()
        msg_data = msg.as_bytes()
        try:
            # Decode quoted-printable content to show plaintext URLs on a single line
            decoded_data = quopri.decodestring(msg_data).decode('utf-8', errors='ignore')
            self.stream.write(decoded_data)
            self.stream.write('\n' + '-' * 79 + '\n')
            self.stream.flush()
        except Exception:
            # Fallback to standard console output
            super().write_message(message)
