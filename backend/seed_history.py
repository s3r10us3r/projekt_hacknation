import random
import uuid
import io
import csv
import hashlib
import sqlite3
from datetime import datetime, timedelta, date

# Import funkcji z Twojego modułu db
from api.db import (
    create_lost_items_table, 
    create_office_accounts_table, 
    create_records_table,
    save_office_account_to_sqlite, 
    insert_lost_item, 
    get_all_lost_items, 
    insert_ds,
    DATABASE_NAME
)
from api.office_account import hash_password

# --- KLASY POMOCNICZE (DTO) ---
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
                 data_publikacji, kategoria, opis, miejsce_znalezienia, 
                 adres_odbioru, email_kontaktowy, 
                 telefon_kontaktowy, status):
        self.id_ewidencyjny = id_ewidencyjny
        self.powiat = powiat
        self.data_znalezienia = data_znalezienia
        self.data_przekazania = data_przekazania
        self.data_publikacji = data_publikacji
        self.kategoria = kategoria
        self.opis = opis
        self.miejsce_znalezienia = miejsce_znalezienia 
        self.adres_odbioru = adres_odbioru
        self.email_kontaktowy = email_kontaktowy
        self.telefon_kontaktowy = telefon_kontaktowy
        self.status = status

# --- GENERATOR CSV I MD5 ---
def generate_csv_string(powiat_slug):
    """
    Generuje treść CSV na podstawie aktualnego stanu bazy dla danego powiatu.
    """
    lost_items = get_all_lost_items(powiat=powiat_slug)
    
    field_names = [
        'id_ewidencyjny', 'powiat', 'data_znalezienia', 'data_przekazania',
        'data_publikacji', 'kategoria', 'opis', 'miejsce_znalezienia',
        'adres_odbioru', 'email_kontaktowy', 'telefon_kontaktowy', 'status'
    ]

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=field_names, delimiter=';')
    writer.writeheader()
    
    if lost_items:
        for item in lost_items:
            # Bezpieczne mapowanie pól (zabezpieczenie przed brakiem klucza)
            row_to_write = {k: item.get(k, '') for k in field_names}
            writer.writerow(row_to_write)

    csv_content = output.getvalue()
    output.close()
    return csv_content

def get_md5(data_string):
    encoded_data = data_string.encode('utf-8')
    return hashlib.md5(encoded_data).hexdigest()

# --- CZYSZCZENIE BAZY ---
def reset_database():
    """Usuwa tabele, aby zapewnić czysty start."""
    print("🧹 Czyszczenie starej bazy danych...")
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS lost_items")
    cursor.execute("DROP TABLE IF EXISTS office_accounts")
    cursor.execute("DROP TABLE IF EXISTS records")
    conn.commit()
    conn.close()

# --- GŁÓWNA LOGIKA ---
def seed_history():
    # 1. Wyczyść bazę (zakładamy pustą, więc usuwamy stare śmieci)
    reset_database()

    print("🌱 Rozpoczynam generowanie historii dla Warszawy...")

    # 2. Utwórz tabele na nowo
    create_office_accounts_table()
    create_lost_items_table()
    create_records_table()

    # 3. Utwórz konto Warszawy (Bez sprawdzania authenticate_user, bo baza jest pusta)
    warsaw_data = {
        "city": "warszawa", "name": "Biuro Rzeczy Znalezionych Warszawa",
        "prefix": "WA", "email": "rzeczy@um.warszawa.pl", "phone": "+48 22 444 55 66",
        "addr": "ul. Dzielna 15, 00-100 Warszawa"
    }

    warsaw_account = MockOffice(
        user_id=str(uuid.uuid4()),
        login=warsaw_data['email'],
        hashed_password=hash_password('user123'),
        office_name=warsaw_data['name'],
        contact_email=warsaw_data['email'],
        contact_phone=warsaw_data['phone'],
        address=warsaw_data['addr'],
        powiat=warsaw_data['city'],
        id_prefix=warsaw_data['prefix']
    )
    
    save_office_account_to_sqlite(warsaw_account)
    print("🏢 Utworzono urząd: Warszawa")

    # 4. Pętla Czasowa (Dziś, Wczoraj, Przedwczoraj)
    # Generujemy dane chronologicznie, żeby CSV "rósł" z każdym dniem.
    
    categories = ["Elektronika", "Dokumenty", "Klucze", "Inne", "Odzież"]
    descriptions = ["Znaleziono w metrze", "Zostawione w parku", "Znalezione przy urzędzie", "Leżało na ławce"]
    
    today = date.today()
    # Kolejność: 2 dni temu -> Wczoraj -> Dziś
    timeline = [
        today - timedelta(days=2),
        today - timedelta(days=1),
        today
    ]

    item_counter = 1

    for target_date in timeline:
        date_str = target_date.strftime("%Y-%m-%d")
        print(f"\n📅 Przetwarzanie daty: {date_str}...")

        # A. Wygeneruj 10 przedmiotów dla tej konkretnej daty
        for _ in range(10):
            
            item = MockItem(
                # Unikalne ID zależne od daty i licznika
                id_ewidencyjny=f"{warsaw_account.id_prefix}/{target_date.year}/{date_str.replace('-','')}-{item_counter:04d}",
                powiat=warsaw_account.powiat,
                data_znalezienia=date_str, # Znaleziono w tym dniu
                data_przekazania=date_str,
                data_publikacji=date_str,  # Opublikowano w tym dniu
                kategoria=random.choice(categories),
                opis=f"{random.choice(descriptions)} - Przedmiot nr {item_counter}",
                miejsce_znalezienia="Centrum Warszawy",
                adres_odbioru=warsaw_account.address,
                email_kontaktowy=warsaw_account.contact_email,
                telefon_kontaktowy=warsaw_account.contact_phone,
                status="do_odbioru"
            )
            
            insert_lost_item(item)
            item_counter += 1

        print(f"   ✅ Dodano 10 nowych przedmiotów (Razem w bazie: {item_counter - 1})")

        # B. Wygeneruj migawkę (Snapshot) CSV
        # Pobiera WSZYSTKIE przedmioty z bazy dla tego powiatu (czyli z tego dnia + dni poprzednich)
        csv_content = generate_csv_string(warsaw_account.powiat)
        
        # C. Oblicz MD5
        md5_sum = get_md5(csv_content)
        
        # D. Zapisz historię w tabeli records
        # insert_ds(checksum, data, date_str, powiat)
        if insert_ds(md5_sum, csv_content, date_str, warsaw_account.powiat):
            print(f"   💾 Zapisano historyczny dataset dla {date_str} | MD5: {md5_sum[:8]}...")
        else:
            print(f"   ⚠️ Błąd zapisu datasetu dla {date_str}")

    print("\n🚀 Generowanie historii zakończone sukcesem!")

if __name__ == "__main__":
    seed_history()
