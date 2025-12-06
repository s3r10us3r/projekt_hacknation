import sqlite3
from api.office_account import hash_password

DATABASE_NAME = 'hackathon_data.db'


def create_office_accounts_table():
    """Creates the necessary SQLite table for office accounts."""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS office_accounts (
                user_id TEXT PRIMARY KEY,
                login TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                office_name TEXT,
                contact_email TEXT,
                contact_phone TEXT,
                address TEXT,
                powiat TEXT,
                id_prefix TEXT
            );
        """)
        conn.commit()
        print("✅ SQLite table 'office_accounts' ready.")
        return True
    except sqlite3.Error as e:
        print(f"❌ Błąd SQLite podczas tworzenia tabeli: {e}")
        return False
    finally:
        if conn:
            conn.close()


def save_office_account_to_sqlite(account_object):
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        data_to_insert = (
            account_object.user_id,
            account_object.login,
            account_object.hashed_password,
            account_object.office_name,
            account_object.contact_email,
            account_object.contact_phone,
            account_object.address,
            account_object.powiat,
            account_object.id_prefix,
        )

        sql_query = "INSERT INTO office_accounts VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)"
        cursor.execute(sql_query, data_to_insert)
        conn.commit()
        print('no error')
        return True
    except sqlite3.IntegrityError as e:
        print("Error ", e)
        return False
    except sqlite3.Error as e:
        print('error ', e)
        return False
    finally:
        if conn:
            conn.close()


def authenticate_user(login, password):
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM office_accounts WHERE login = ?", (login,))
        account_row = cursor.fetchone()
        if account_row is False:
            print('account_row is false')
            return None
        provided_hash = hash_password(password)
        stored_hash = account_row['hashed_password']
        if provided_hash == stored_hash:
            return dict(account_row)
        else:
            return None
    except sqlite3.Error as e:
        print("Błąd SQLite podczas autoryzacji", e)
    finally:
        if conn:
            conn.close()


def create_lost_items_table():
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        # SQLITE TWORZENIE TABELI
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lost_items (
                id_ewidencyjny TEXT PRIMARY KEY NOT NULL,  
                data_znalezienia TEXT NOT NULL,
                data_przekazania TEXT,
                data_publikacji TEXT NOT NULL,
                kategoria TEXT NOT NULL,
                opis TEXT NOT NULL,
                powiat TEXT NOT NULL,
                adres_znalezienia TEXT,
                adres_znalezienia_opis TEXT,
                adres_odbioru TEXT NOT NULL,
                email_kontaktowy TEXT NOT NULL,
                telefon_kontaktowy TEXT NOT NULL,
                status TEXT NOT NULL
            );
        """)
        conn.commit()
        print("✅ SQLite tabela 'lost_items' gotowa.")
        return True
    except sqlite3.Error as e:
        print(f"❌ Błąd SQLite podczas tworzenia tabeli: {e}")
        return False
    finally:
        if conn:
            conn.close()


def insert_lost_item(lost_item):
    """
    Wstawia obiekt klasy LostItem do bazy danych.
    """
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        # Przygotowanie krotki z danymi w kolejności odpowiadającej kolumnom
        data_to_insert = (
            lost_item.id_ewidencyjny,
            lost_item.data_znalezienia,
            lost_item.data_przekazania,
            lost_item.data_publikacji,
            lost_item.kategoria,
            lost_item.opis,
            lost_item.powiat,
            lost_item.adres_znalezienia,
            lost_item.adres_znalezienia_opis,
            lost_item.adres_odbioru,
            lost_item.email_kontaktowy,
            lost_item.telefon_kontaktowy,
            lost_item.status
        )

        # Jawne wymienienie kolumn to dobra praktyka (chroni przed zmianą kolejności w bazie)
        sql_query = """
            INSERT INTO lost_items (
                id_ewidencyjny, data_znalezienia, data_przekazania, data_publikacji,
                kategoria, opis, powiat, adres_znalezienia, adres_znalezienia_opis,
                adres_odbioru, email_kontaktowy, telefon_kontaktowy, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        cursor.execute(sql_query, data_to_insert)
        conn.commit()
        print(f"✅ Dodano zgubę: {lost_item.id_ewidencyjny}")
        return True

    except sqlite3.IntegrityError as e:
        print(f"❌ Błąd integralności (np. duplikat ID): {e}")
        return False
    except sqlite3.Error as e:
        print(f"❌ Błąd SQLite podczas dodawania zguby: {e}")
        return False
    finally:
        if conn:
            conn.close()


def get_lost_item_by_id(id_ewidencyjny):
    """
    Fetches a single lost item from the database by its unique ID.
    Returns a dictionary if found, or None if not found.
    """
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        conn.row_factory = sqlite3.Row 
        cursor = conn.cursor()
        sql_query = "SELECT * FROM lost_items WHERE id_ewidencyjny = ?"
        cursor.execute(sql_query, (id_ewidencyjny,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        else:
            return None

    except sqlite3.Error as e:
        print(f"❌ SQLite Error while fetching item {id_ewidencyjny}: {e}")
        return None
    finally:
        if conn:
            conn.close()


def update_lost_item(lost_item):
    """
    Updates an existing lost item in the database based on id_ewidencyjny.
    """
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        # SQL Update Query
        # We update every field EXCEPT the ID (which is used to find the record)
        sql_query = """
            UPDATE lost_items
            SET
                data_znalezienia = ?,
                data_przekazania = ?,
                data_publikacji = ?,
                kategoria = ?,
                opis = ?,
                powiat = ?,
                adres_znalezienia = ?,
                adres_znalezienia_opis = ?,
                adres_odbioru = ?,
                email_kontaktowy = ?,
                telefon_kontaktowy = ?,
                status = ?
            WHERE id_ewidencyjny = ?
        """

        # Prepare the data tuple. 
        # CRITICAL: The order must match the SET clause, and id_ewidencyjny must be LAST.
        data_to_update = (
            lost_item.data_znalezienia,
            lost_item.data_przekazania,
            lost_item.data_publikacji,
            lost_item.kategoria,
            lost_item.opis,
            lost_item.powiat,
            lost_item.adres_znalezienia,
            lost_item.adres_znalezienia_opis,
            lost_item.adres_odbioru,
            lost_item.email_kontaktowy,
            lost_item.telefon_kontaktowy,
            lost_item.status,
            lost_item.id_ewidencyjny  # <--- ID goes here for the WHERE clause
        )

        cursor.execute(sql_query, data_to_update)
        conn.commit()

        # Check if a row was actually found and updated
        if cursor.rowcount == 0:
            print(f"⚠️ Warning: No item found with ID {lost_item.id_ewidencyjny} to update.")
            return False
        
        print(f"✅ Updated item: {lost_item.id_ewidencyjny}")
        return True

    except sqlite3.Error as e:
        print(f"❌ SQLite Error during update: {e}")
        return False
    finally:
        if conn:
            conn.close()
