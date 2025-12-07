import random
import uuid
from datetime import datetime, timedelta
from api.db import create_lost_items_table, create_office_accounts_table, save_office_account_to_sqlite, insert_lost_item
from api.office_account import hash_password

class MockOffice:
    def __init__(self, user_id, login, hashed_password, office_name, contact_email, 
                 contact_phone, address, powiat, id_prefix):
        self.user_id = user_id
        self.login = login
        self.hashed_password = hashed_password
        self.office_name = office_name
        self.contact_email = contact_email
        self.contact_phone = contact_phone
        self.address = address
        self.powiat = powiat
        self.id_prefix = id_prefix

class MockItem:
    def __init__(self, id_ewidencyjny, powiat, data_znalezienia, data_przekazania, 
                 data_publikacji, kategoria, opis, adres_znalezienia, 
                 adres_znalezienia_opis, adres_odbioru, email_kontaktowy, 
                 telefon_kontaktowy, status):
        self.id_ewidencyjny = id_ewidencyjny
        self.powiat = powiat
        self.data_znalezienia = data_znalezienia
        self.data_przekazania = data_przekazania
        self.data_publikacji = data_publikacji
        self.kategoria = kategoria
        self.opis = opis
        self.adres_znalezienia = adres_znalezienia
        self.adres_znalezienia_opis = adres_znalezienia_opis
        self.adres_odbioru = adres_odbioru
        self.email_kontaktowy = email_kontaktowy
        self.telefon_kontaktowy = telefon_kontaktowy
        self.status = status

# --- GENERATOR DANYCH ---

def seed_database():
    print("🌱 Rozpoczynam sianie danych (seeding)...")
    
    # 1. Inicjalizacja tabel
    create_office_accounts_table()
    create_lost_items_table()

    # 2. Tworzenie 3 Urzędów
    offices_data = [
        {
            "city": "warszawa", "name": "Biuro Rzeczy Znalezionych Warszawa",
            "prefix": "WA", "email": "rzeczy@um.warszawa.pl", "phone": "+48 224445566",
            "addr": "ul. Dzielna 15, 00-100 Warszawa"
        },
        {
            "city": "krakow", "name": "Urząd Miasta Krakowa - Zguby",
            "prefix": "KR", "email": "kontakt@krakow.pl", "phone": "+48 126161234",
            "addr": "Wielopole 17a, 31-072 Kraków"
        },
        {
            "city": "gdansk", "name": "Starostwo Powiatowe w Gdańsku",
            "prefix": "GD", "email": "biuro@powiat-gdanski.pl", "phone": "+48 587731212",
            "addr": "ul. Wojska Polskiego 16, 83-000 Pruszcz Gdański"
        }
    ]

    created_offices = []

    for office in offices_data:
        # Symulacja hashowania hasła (lub użyj swojej funkcji hash_password)
        dummy_hash = hash_password('user123')
        account = MockOffice(
            user_id=str(uuid.uuid4()),
            login=office['email'],
            hashed_password=dummy_hash,
            office_name=office['name'],
            contact_email=office['email'],
            contact_phone=office['phone'],
            address=office['addr'],
            powiat=office['city'],
            id_prefix=office['prefix']
        )
        if save_office_account_to_sqlite(account):
            created_offices.append(account)
            print(f"   🏢 Dodano urząd: {office['name']}")

    # 3. Tworzenie 30 Rzeczy Znalezionych
    categories = ["Elektronika", "Dokumenty", "Klucze", "Odzież", "Inne", "Biżuteria"]
    descriptions = ["Znaleziono na ławce w parku", "Zostawione w autobusie", "Leżało na chodniku", "Znalezione w urzędzie", "Brak cech szczególnych"]
    statuses = ["published", "archived", "returned"]

    for i in range(1, 31):
        # Losujemy urząd, do którego przypiszemy rzecz
        office = random.choice(created_offices)
        # Generowanie dat
        days_ago = random.randint(0, 60)
        found_date = datetime.now() - timedelta(days=days_ago)
        pub_date = found_date + timedelta(days=random.randint(0, 2))
        # Formatowanie dat na string (SQLite przechowuje TEXT)
        date_zn_str = found_date.strftime("%Y-%m-%d")
        date_pub_str = pub_date.strftime("%Y-%m-%d")
        # POLA OPCJONALNE (NULLABLE) - losowo puste
        # Data przekazania: 50% szans na brak (np. znaleziona przez pracownika, a nie przyniesiona)
        date_przekazania = None
        if random.choice([True, False]):
            date_przekazania = date_zn_str
            
        miejsce_znalezienia = None
        # Adres znalezienia: 30% szans na brak (ktoś nie podał)
        if random.random() > 0.5:
            miejsce_znalezienia = 'miejsce znalezienia :)'

        item = MockItem(
            id_ewidencyjny=f"{office.id_prefix}/{found_date.year}/{i:04d}",
            powiat=office.powiat,
            data_znalezienia=date_zn_str,
            data_przekazania=date_przekazania, # Może być None
            data_publikacji=date_pub_str,
            kategoria=random.choice(categories),
            opis=f"{random.choice(descriptions)} - przedmiot nr {i}",
            miejsce_znalezienia=miejsce_znalezienia,
            adres_odbioru=office.address,
            email_kontaktowy=office.contact_email,
            telefon_kontaktowy=office.contact_phone,
            status=random.choice(statuses)
        )

        insert_lost_item(item)

    print("✅ Zakończono! Baza została zasilona 3 urzędami i 30 przedmiotami.")

if __name__ == "__main__":
    seed_database()
