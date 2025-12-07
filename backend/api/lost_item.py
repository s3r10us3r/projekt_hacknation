from datetime import datetime
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from api.schema import LOST_ITEM_SCHEMA
from random import randint
import json


class LostItem:
    """Klasa reprezentująca pojedynczą rzecz znalezioną."""

    def __init__(self, item_data: dict, id_prefix: str, powiat: str, adres_odbioru: str, email: str, phone: str):
        print('LOST ITEM CONSTRUCTOR', powiat)
        """
        Inicjalizacja obiektu z danymi wejściowymi i automatyczne
        uzupełnianie pól (np. z sesji urzędnika).
        """
        # Uzupełnianie pól z sesji/backendu
        self.id_ewidencyjny = self._generate_id(id_prefix)  # Automatycznie generowany ID
        self.data_publikacji = datetime.now().isoformat()  # Format ISO 8601 z czasem
        self.powiat = powiat
        self.data_znalezienia = item_data.get('data_znalezienia')
        self.data_przekazania = item_data.get('data_przekazania')
        self.kategoria = item_data.get('kategoria')
        self.opis = item_data.get('opis')
        self.miejsce_znalezienia = item_data.get('miejsce_znalezienia')
        self.adres_odbioru = adres_odbioru
        self.email_kontaktowy = email
        self.telefon_kontaktowy = phone
        self.status = item_data.get('status')

    def _generate_id(self, prefix: str) -> str:
        year = datetime.now().strftime("%Y")
        num = randint(1, 10_000)
        num_str = str(num)
        padded_str = num_str.zfill(4)
        return f"{prefix}-{year}-{padded_str}"

    def to_dict(self) -> dict:
        """Konwertuje obiekt na słownik gotowy do walidacji lub zapisu."""
        return self.__dict__

    def validate(self):
        """
        Waliduje wewnętrzne dane obiektu względem zdefiniowanej JSON Schemy.
        Zgłasza wyjątek ValidationError, jeśli walidacja nie powiedzie się.
        """
        data = self.to_dict()
        try:
            # Użycie funkcji validate z jsonschema
            schema_dict = json.loads(LOST_ITEM_SCHEMA)
            validate(instance=data, schema=schema_dict)
            return True, ''
        except ValidationError as e:
            # Zgłoś błąd walidacji, który aplikacja Flask może przechwycić
            print(e.message, e.path)
            return False, list(e.path)
        except Exception as e:
            # Błędy formatu (np. daty)
            raise ValidationError(f"Ogólny błąd walidacji: {e}")
