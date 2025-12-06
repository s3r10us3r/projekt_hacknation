import requests
import sqlite3
import os

# Konfiguracja
BASE_URL = "http://127.0.0.1:5000"
DB_PATH = "hackathon_data.db"

# Dane logowania (z twojego seed_data)
EMAIL = "warszawa@um.pl"
PASSWORD = "user123"

def print_step(message):
    print(f"\n🔹 {message}")

def print_ok(message):
    print(f"✅ {message}")

def print_err(message):
    print(f"❌ {message}")

def get_latest_item_id():
    """
    Pomocnicza funkcja: Ponieważ endpoint POST nie zwraca ID,
    musimy zajrzeć do bazy, żeby wiedzieć co testować w krokach GET/PUT.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id_ewidencyjny FROM lost_items ORDER BY rowid DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None
    except Exception as e:
        print_err(f"Nie udało się pobrać ID z bazy: {e}")
        return None

def run_tests():
    # Tworzymy sesję, aby przechowywać pliki cookie (zalogowanie)
    session = requests.Session()

    # 1. Health Check
    print_step("Testowanie: GET /")
    try:
        r = session.get(f"{BASE_URL}/")
        if r.status_code == 201:
            print_ok(f"Server żyje: {r.json()}")
        else:
            print_err(f"Status: {r.status_code}")
    except requests.exceptions.ConnectionError:
        print_err("Nie można połączyć się z serwerem. Czy uruchomiłeś 'app.py'?")
        return

    # 2. Logowanie
    print_step("Testowanie: POST /login")
    login_payload = {
        "email": EMAIL,
        "password": PASSWORD
    }
    r = session.post(f"{BASE_URL}/login", json=login_payload)
    if r.status_code == 200:
        print_ok("Zalogowano pomyślnie. Sesja utworzona.")
    else:
        print_err(f"Błąd logowania: {r.text}")
        return # Nie ma sensu iść dalej bez logowania

    # 3. Dodawanie rzeczy (POST)
    print_step("Testowanie: POST /lost_item")
    item_payload = {
        "data_znalezienia": "2023-12-06",
        "data_przekazania": "2023-12-07",
        "kategoria": "elektronika",
        "opis": "Testowy Laptop Dell (wysłany requestem)",
        "powiat": "Warszawa", # Backend powinien to nadpisać z sesji, ale wysyłamy dla walidacji
        "adres_znalezienia": "Dworzec Centralny",
        "adres_znalezienia_opis": "Peron 3",
        "adres_odbioru": "Biuro Rzeczy Znalezionych",
        "email_kontaktowy": EMAIL,
        "telefon_kontaktowy": "+48 223430000",
        "status": "do_odbioru"
    }
    
    r = session.post(f"{BASE_URL}/lost_item", json=item_payload)
    if r.status_code in [200, 201]:
        print_ok("Utworzono przedmiot.")
    else:
        print_err(f"Błąd tworzenia: {r.status_code} - {r.text}")

    # 4. Pobieranie ID utworzonego przedmiotu
    # API nie zwraca ID w odpowiedzi, więc hackujemy to zapytaniem do SQL,
    # żeby móc przetestować endpointy GET i PUT.
    item_id = get_latest_item_id()
    if not item_id:
        print_err("Nie znaleziono przedmiotu w bazie. Przerywam.")
        return
    print(f"   (Znaleziono ID do testów: {item_id})")

    # 5. Pobieranie szczegółów (GET)
    print_step(f"Testowanie: GET /lost_item/{item_id}")
    r = session.get(f"{BASE_URL}/lost_item/{item_id}")
    if r.status_code in [200, 201]:
        data = r.json()
        if data['opis'] == "Testowy Laptop Dell (wysłany requestem)":
            print_ok("Pobrano poprawne dane przedmiotu.")
        else:
            print_err("Dane się nie zgadzają.")
    else:
        print_err(f"Błąd pobierania: {r.status_code}")

    # 6. Aktualizacja (PUT)
    print_step(f"Testowanie: PUT /lost_item/{item_id}")
    
    # Pobieramy obecne dane i zmieniamy opis
    update_payload = r.json() 
    update_payload['opis'] = "Testowy Laptop Dell - ZAKTUALIZOWANY PRZEZ PUT"
    update_payload['status'] = "odebrano"

    r = session.put(f"{BASE_URL}/lost_item/{item_id}", json=update_payload)
    
    if r.status_code == 200:
        print_ok("Zaktualizowano przedmiot.")
    elif r.status_code == 405:
        print_err("Błąd 405. Sprawdź w app.py czy masz methods=['POST', 'PUT'] (lista), a nie 'POST, PUT' (string).")
    else:
        print_err(f"Błąd aktualizacji: {r.status_code} - {r.text}")

    # Sprawdzenie czy się zmieniło
    check = session.get(f"{BASE_URL}/lost_item/{item_id}").json()
    if check['status'] == 'odebrano':
         print_ok("Weryfikacja: Status w bazie to 'odebrano'.")

    # 7. Upload pliku / AI Mock
    print_step("Testowanie: POST /form_autocomplete (Upload pliku)")
    
    # Tworzymy tymczasowy plik
    with open("temp_img.jpg", "wb") as f:
        f.write(b"fake image data")

    files = {'photos': open('temp_img.jpg', 'rb')}
    r = session.post(f"{BASE_URL}/form_autocomplete", files=files)
    
    if r.status_code == 201:
        resp = r.json()
        if resp.get('kategoria') == 'pieniadze':
            print_ok(f"AI odpowiedziało: {resp}")
        else:
            print_err(f"Zła odpowiedź AI: {resp}")
    else:
        print_err(f"Błąd uploadu: {r.status_code}")
    
    # Sprzątanie
    os.remove("temp_img.jpg")

if __name__ == "__main__":
    print("--- START TESTÓW SIECIOWYCH ---")
    run_tests()
    print("\n--- KONIEC ---")
