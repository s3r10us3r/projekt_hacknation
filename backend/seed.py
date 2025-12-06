from api.office_account import OfficeAccount
from api.db import create_office_accounts_table, save_office_account_to_sqlite

def seed_data():
    print("Rozpoczynam wstępne zasilanie bazy danych...")
    create_office_accounts_table()

    offices_to_add = [
        OfficeAccount(
            login="warszawa@um.pl",
            password="user123",
            office_name="Urząd Miasta Stołecznego Warszawy",
            contact_email="biuro.rzeczy@warszawa.pl",
            contact_phone="+48 22 443 00 00",
            address="ul. Dzielna 15, 00-162 Warszawa",
            powiat="Warszawa",
            prefix="UM-WAW"
        ),
        OfficeAccount(
            login="krakow@um.pl",
            password="user123",
            office_name="Urząd Miasta Krakowa",
            contact_email="brz@um.krakow.pl",
            contact_phone="+48 12 616 12 12",
            address="os. Zgody 2, 31-949 Kraków",
            powiat="Krakowski",
            prefix="UM-KRAK"
        ),
        OfficeAccount(
            login="pcim@ug.pl",
            password="user123",
            office_name="Urząd Gminy Pcim",
            contact_email="gmina@pcim.pl",
            contact_phone="+48 12 274 80 50",
            address="Pcim 563, 32-432 Pcim",
            powiat="Myślenicki",
            prefix="UG-PCIM"
        )
    ]

    # 3. Pętla zapisująca do bazy
    count = 0
    for office in offices_to_add:
        # Funkcja save_office_account_to_sqlite oczekuje obiektu OfficeAccount
        if save_office_account_to_sqlite(office):
            count += 1
        else:
            print(f"⚠️  Pominięto (prawdopodobnie duplikat loginu): {office.login}")

    print(f"\n✅ Zakończono! Dodano {count} nowych urzędów.")
    print("👉 Dane testowe: warszawa@um.pl / user123")

if __name__ == "__main__":
    seed_data()
