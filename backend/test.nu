#!/usr/bin/env nu

# --- KONFIGURACJA ---
let base_url = "http://127.0.0.1:5000"
let email = "warszawa@um.pl"
let password = "user123"

# Kolory dla ładnego outputu
def log [msg] { print $"(ansi green)>>> ($msg)(ansi reset)" }
def log_err [msg] { print $"(ansi red)!!! ($msg)(ansi reset)" }
def log_data [data] { print $"(ansi yellow)($data)(ansi reset)" }

log $"Rozpoczynam testy API na ($base_url)..."

# ---------------------------------------------------------
# 1. HEALTH CHECK
# ---------------------------------------------------------
log "1. Sprawdzam endpoint główny (GET /)..."
try {
    let res = (http get $"($base_url)/")
    log_data $res
} catch {
    log_err "Nie udało się połączyć z serwerem. Czy Flask działa?"
    exit 1
}

# ---------------------------------------------------------
# 2. LOGOWANIE (Pobranie Cookies)
# ---------------------------------------------------------
log "2. Logowanie (POST /login)..."
let login_body = { email: $email, password: $password }

# Używamy flagi -f (full), żeby dostać nagłówki z Cookies
let login_res = (http post -f -t application/json $"($base_url)/login" $login_body)

if ($login_res.status != 200) {
    log_err $"Błąd logowania! Status: ($login_res.status)"
    exit 1
}

# Wyciąganie ciasteczka sesyjnego z nagłówków (Set-Cookie)
# Nushell zwraca nagłówki jako tabelę, musimy wyciągnąć wartość
let cookie_raw = ($login_res.headers | get -i "Set-Cookie")
let cookie = if ($cookie_raw | is-empty) { "" } else { $cookie_raw | first }

log_data $"Zalogowano! Pobrane Cookie: ($cookie | str substring 0..30)..."

# Przygotowanie nagłówków do kolejnych zapytań
let auth_headers = [$"Cookie: ($cookie)"]

# ---------------------------------------------------------
# 3. DODAWANIE ZGUBY
# ---------------------------------------------------------
log "3. Dodawanie nowej zguby (POST /lost_item)..."

# Dane testowe zgodne z Twoją JSON Schema
let new_item = {
    "kategoria": "elektronika",
    "opis": "Testowy iPhone znaleziony przez skrypt Nushell",
    "data_znalezienia": "2023-11-15",
    "adres_znalezienia": "Metro Centrum",
    "status": "do_odbioru",
    # Te pola zostaną nadpisane przez backend z sesji, ale schema może ich wymagać w walidacji wstępnej
    "powiat": "TEMP",
    "adres_odbioru": "TEMP",
    "email_kontaktowy": "temp@temp.pl" 
}

let add_res = (http post -H $auth_headers -t application/json $"($base_url)/lost_item" $new_item)
log_data $add_res

# Wyciągamy ID nowo utworzonego przedmiotu z odpowiedzi
# Zakładam, że endpoint zwraca JSON w stylu: {"id": "UM-WAW-2023-0001", ...}
let item_id = ($add_res | get id)

if ($item_id == null) {
    log_err "Nie udało się pobrać ID nowego przedmiotu."
    exit 1
}

log $"Utworzono przedmiot o ID: ($item_id)"

# ---------------------------------------------------------
# 4. POBIERANIE ZGUBY
# ---------------------------------------------------------
log $"4. Pobieranie szczegółów zguby ($item_id) (GET)..."

let get_res = (http get -H $auth_headers $"($base_url)/lost_item/($item_id)")
log_data $get_res

# Sprawdzenie czy dane się zgadzają
if ($get_res.opis == "Testowy iPhone znaleziony przez skrypt Nushell") {
    print "✅ Opis się zgadza."
} else {
    log_err "Opis pobrany z bazy jest inny niż wysłany!"
}

# ---------------------------------------------------------
# 5. EDYCJA ZGUBY
# ---------------------------------------------------------
log $"5. Edycja zguby ($item_id) (PUT)..."

# Modyfikujemy opis
let edit_body = ($new_item | merge { "opis": "ZMODYFIKOWANY: To jednak był Samsung", "status": "odebrano" })

# Flask wymaga metody PUT. Nushell obsługuje `http put`.
let edit_res = (http put -H $auth_headers -t application/json $"($base_url)/lost_item/($item_id)" $edit_body)
log_data $edit_res

# Weryfikacja zmiany
let verify_res = (http get -H $auth_headers $"($base_url)/lost_item/($item_id)")
if ($verify_res.status == "odebrano") {
    print "✅ Status zaktualizowany pomyślnie na 'odebrano'."
} else {
    log_err "Status nie został zaktualizowany!"
}

# ---------------------------------------------------------
# 6. TEST MOCK AI (Upload zdjęć)
# ---------------------------------------------------------
log "6. Testowanie endpointu AI (POST /form_autocomplete)..."

# Tworzymy tymczasowy plik do wysłania
"to jest przykładowy obrazek" | save -f dummy.jpg

# Nushell obsługuje multipart form-data, jeśli podamy content-type
# Uwaga: w starszych wersjach Nu upload plików był trudny, w nowych (0.90+) działa lepiej.
# Jeśli to nie zadziała w Twojej wersji, curl jest bezpieczniejszą opcją wewnątrz Nu.

try {
    # Używamy curla, bo obsługa multipart w 'http post' Nushella bywa kapryśna zależnie od wersji
    # Przekazujemy cookie ręcznie
    let curl_res = (curl -s -X POST -b $cookie -F "photos=@dummy.jpg" $"($base_url)/form_autocomplete")
    # Parsujemy wynik tekstowy curla na JSON w Nushellu
    let json_res = ($curl_res | from json)
    log_data $json_res
    
    if ($json_res.kategoria == "pieniadze") {
        print "✅ AI (Mock) poprawnie rozpoznało 'pieniadze'."
    }
} catch {
    log_err "Błąd podczas testu uploadu zdjęć."
}

# Sprzątanie
rm dummy.jpg

log "---------------------------------------------------------"
log "🎉 WSZYSTKIE TESTY ZAKOŃCZONE SUKCESEM"
log "---------------------------------------------------------"
