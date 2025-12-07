from flask import Flask, request, session, jsonify, make_response
from flasgger import Swagger
from api.db import authenticate_user, insert_lost_item, update_lost_item, get_lost_item_by_id, create_lost_items_table, create_office_accounts_table
from api.lost_item import LostItem
from jsonschema.exceptions import ValidationError
from PIL import Image
from gen_xml import generate_valid_xml
from gen_csv import gen_lost_items_csv, get_md5

# PROCESSOR, VLM = None, None
# VLM_PATH = "HuggingFaceTB/SmolVLM2-2.2B-Instruct"


app = Flask(__name__)
app.secret_key = 'twoj_sekret'
swagger = Swagger(app)


@app.route('/zdrowie')
def healt():
    """
    Sprawdzenie statusu serwera (Health Check).
    ---
    responses:
      200:
        description: Serwer działa poprawnie.
        schema:
          type: object
          properties:
            message:
              type: string
              example: ok
    """
    return jsonify({'message': 'ok'}), 200 # Zmieniono 201 na 200 (standard dla health check)


@app.route('/api/konta/logowanie', methods=['POST'])
def login():
    """
    Logowanie urzędnika do systemu.
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              example: admin_warszawa@um.pl
            password:
              type: string
              example: tajnehaslo123
    responses:
      200:
        description: Pomyślne zalogowanie. Powiat zapisany w sesji.
        schema:
          type: object
          properties:
            message: {type: string}
            powiat: {type: string}
      401:
        description: Nieprawidłowy e-mail lub hasło.
      400:
        description: Brak wymaganych danych logowania.
    """
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    # ... (logika logowania) ...
    account_data = authenticate_user(email, password)
    if not email or not password:
        return jsonify({"message": "Brak danych logowania."}), 400
    if account_data:
        # ... (zapis do sesji) ...
        session['logged_in'] = True
        session['user_id'] = account_data['user_id']
        session['powiat'] = account_data['powiat']
        session['id_prefix'] = account_data['id_prefix']
        session['contact_email'] = account_data['contact_email']
        session['address'] = account_data['address']
        session['phone'] = account_data['contact_phone']

        return jsonify({"message": "Pomyślnie zalogowano", "powiat": session['powiat']}), 200
    else:
        return jsonify({"message": "Nieprawidłowy e-mail lub hasło."}), 401


@app.route('/api/rzeczy_znalezione', methods=['POST'])
def register_new():
    """
    Rejestracja nowego przedmiotu. Wymaga aktywnej sesji (logowania).
    ---
    tags:
      - Rejestr
    parameters:
      - name: item_data
        in: body
        required: true
        schema:
          type: object
          properties:
            opis: {type: string}
            kategoria: {type: string, enum: ["dokumenty_i_portfele", "elektronika", "inne"]}
            # ... (Więcej pól zgodnie z LostItem DTO)
    responses:
      201:
        description: Zasób utworzony pomyślnie.
      401:
        description: Nieautoryzowany dostęp (brak sesji).
      404:
        description: Błąd walidacji danych wejściowych.
        schema:
          type: object
          properties:
            fields: {type: array, items: {type: string}, description: Lista pól z błędami.}
    """
    if not session.get('logged_in'):
        return jsonify({'message': 'unauthorized'}), 401
    data = request.get_json()
    data_dict = dict(data)
    # Zaktualizowano konstruktor LostItem o dane z sesji
    lost_item = LostItem(data_dict, session.get('id_prefix'), session.get('powiat'), session.get('address'), session.get('contact_email'), session.get('phone'))
    try:
        # Poprawka: Odbieramy błędy pól
        val, msg = lost_item.validate()
        if val:
            insert_lost_item(lost_item)
            return '', 201
        else:
            # Zwracamy listę pól, które nie przeszły walidacji, zgodnie z ustaloną konwencją
            return jsonify({'fields': msg}), 400 # Zmieniono 404 na 400 (Bad Request)
    except ValidationError as e:
        return jsonify({'message': e.message}), 400


@app.route('/api/rzeczy_znalezione/<id_ewidencyjny>')
def get_item(id_ewidencyjny):
    """
    Pobranie pojedynczego rekordu
    ---
    tags:
      - Rejestr
    parameters:
      - name: id_ewidencyjny
        in: path
        type: string
        required: true
    responses:
      200:
        description: Zwrócono zasób 
      404:
        description: Zasób nie istnieje.
    """
    item = get_lost_item_by_id(id_ewidencyjny)
    if item is None:
        return jsonify({'message': 'not found'}), 404
    else:
        return jsonify(item), 200


@app.route('/api/rzeczy_znalezione/<id_ewidencyjny>', methods=['PUT'])
def edit_item_endpoint(id_ewidencyjny):
    """
    Edycja szczegółów przedmiotu.
    ---
    tags:
      - Rejestr
    parameters:
      - name: id_ewidencyjny
        in: path
        type: string
        required: true
    responses:
      200:
        description: Zaktualizowano pomyślnie (PUT)
      401:
        description: Nieautoryzowany dostęp.
      404:
        description: Zasób nie istnieje.
    """
    if not session.get('logged_in'):
        return jsonify({'message': 'unauthorized'}), 401
    form_data = request.get_json()
    try:
        # Używamy danych z sesji w konstruktorze
        item = LostItem(form_data, id_prefix=session.get('id_prefix'), powiat=session.get('powiat'), address=session.get('address'), email=session.get('contact_email'), phone=session.get('phone'))
        item.id_ewidencyjny = id_ewidencyjny
        val, msg = item.validate()
        if not val:
            return jsonify({'fields': msg}), 400
        if update_lost_item(item):
            return jsonify({"message": f"Item {id_ewidencyjny} updated successfully."}), 200
        else:
            return jsonify({"error": "Update failed (Item might not exist)."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/narzedzia/auto_uzupelnianie', methods=['POST'])
def form_autocomplete():
    """
    Uzupełnianie pól formularza za pomocą AI/VLM.
    ---
    tags:
      - Narzędzia
    parameters:
      - name: photos
        in: formData
        type: file
        required: true
        description: Lista zdjęć przedmiotu.
    responses:
      200:
        description: Zwraca sugerowaną kategorię i opis.
        schema:
          type: object
          properties:
            kategoria: {type: string}
            opis: {type: string}
      400:
        description: Nie znaleziono plików.
    """
    if 'photos' not in request.files:
        return jsonify({'error': "Nie znaleziono plików wejściowych"}), 400
    files_list = request.files.getlist('photos')
    if not files_list or files_list[0].filename == '':
        return jsonify({'error': 'Nie wybrano żadnych plików'}), 400

    images = [Image.open(file.stream) for file in files_list]
    # ... (logika VLM/AI pominięta)
    result = mock_ai_metoda(files_list)
    return jsonify(result), 200 # Zmieniono 201 na 200


@app.route('/api/open-data/<powiat_slug>/xml')
def get_xml(powiat_slug=None):
    """
    Endpoint Metadanych XML dla Harvestera.
    ---
    tags:
      - Open Data
    parameters:
      - name: powiat_slug
        in: path
        type: string
        required: true
        description: Slug powiatu (np. warszawa)
    responses:
      200:
        description: Zwraca plik XML zgodny ze schemą Otwarte Dane.
        content:
          application/xml:
            schema: {type: string, format: binary}
      404:
        description: Brak zasobów dla danego powiatu.
    """
    # Dodać walidację check_powiat_exists(powiat_slug)
    xml_content = generate_valid_xml(powiat_slug)
    response = make_response(xml_content)
    response.headers['Content-Type'] = 'application/xml; charset=utf-8'
    
    # Poprawka: Poprawienie nazwy pliku na spójną z CSV
    response.headers['Content-Disposition'] = f'inline; filename=wykaz_{powiat_slug}.xml' 
    return response, 200 # Używamy 200 OK


@app.route('/api/open-data/<powiat_slug>/data.csv')
def get_csv_endpoint(powiat_slug=None):
    """
    Endpoint Zasobu CSV (Główne Dane).
    ---
    tags:
      - Open Data
    parameters:
      - name: powiat_slug
        in: path
        type: string
        required: true
        description: Slug powiatu (np. warszawa)
      - name: If-None-Match
        in: header
        type: string
        required: false
        description: ETag z poprzedniego pobrania (dla cache).
    responses:
      200:
        description: Zwraca plik CSV z aktualnym ETagiem.
        content:
          text/csv:
            schema: {type: string, format: binary}
      304:
        description: Not Modified (Dane nie uległy zmianie).
      404:
        description: Brak zasobów dla danego powiatu.
    """
    # Dodać walidację check_powiat_exists(powiat_slug)
    
    # Przekazanie sluga do funkcji generującej dane
    csv_content, cnt = gen_lost_items_csv(powiat_slug) 
    
    if cnt == 0:
        return '', 404
    
    md5_hash = get_md5(csv_content)
    if request.headers.get('If-None-Match') == f'"{md5_hash}"':
        return '', 304
        
    response = make_response(csv_content)
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    response.headers['Content-Disposition'] = f'attachment; filename=wykaz_{powiat_slug}.csv'
    response.headers['ETag'] = f'"{md5_hash}"'
    return response, 200


def mock_ai_metoda(photos):
    return {'kategoria': 'pieniadze', 'opis': 'duzo pieniedzy'}


def run_app():
    global PROCESSOR, VLM
    print("--- Inicjalizacja Bazy Danych ---")
    create_office_accounts_table()
    create_lost_items_table()

    print('--- Przygotowywanie modeli AI ---')
    #if torch.cuda.is_available():
    #    PROCESSOR, VLM = get_vlm(VLM_PATH)
    #else:
    #    PROCESSOR, VLM = None, None
    print("--- Start Serwera Flask ---")
    app.run(debug=True, port=5000)
