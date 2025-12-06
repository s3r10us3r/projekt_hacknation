import uuid
import hashlib


class OfficeAccount():
    def __init__(self, login, password, office_name, contact_phone,
                 contact_email, address, powiat, prefix):
        self.user_id = str(uuid.uuid4())
        self.login = login
        self.hashed_password = hash_password(password)
        self.office_name = office_name
        self.contact_phone = contact_phone
        self.contact_email = contact_email
        self.address = address
        self.powiat = powiat
        self.id_prefix = prefix

    def get_autofill_data(self):
        {
            'email_kontaktowy': self.contact_email,
            'telefon_kontaktowy': self.contact_phone,
            'adres_odbioru': self.address,
            'id_prefix': self.prefix,
            'powiat': self.powiat
        }


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()
