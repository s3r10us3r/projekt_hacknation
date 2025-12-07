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
    return jsonify({'message': 'ok'}), 201

@app.route('/api/konta/logowanie', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({"message": "Brak danych logowania."}), 400

    account_data = authenticate_user(email, password)
    if account_data:
        # Zapisanie kluczowych danych do sesji po udanym logowaniu
        session['logged_in'] = True
        session['user_id'] = account_data['user_id']
        session['powiat'] = account_data['powiat']
        session['id_prefix'] = account_data['id_prefix']
        session['contact_email'] = account_data['contact_email']
        session['address'] = account_data['address']

        return jsonify({"message": "Pomyślnie zalogowano", "powiat": session['powiat']}), 200
    else:
        return jsonify({"message": "Nieprawidłowy e-mail lub hasło."}), 401


@app.route('/lost_item', methods=['POST'])
def register_new():
    if not session.get('logged_in'):
        return jsonify({'message': 'unauthorized'}), 401
    data = request.get_json()
    data_dict = dict(data)
    lost_item = LostItem(data_dict, session.get('id_prefix'), session.get('powiat'))
    try:
        lost_item.validate()
        insert_lost_item(lost_item)
        return 201
    except ValidationError as e:
        return jsonify({'message': e.message}), 404


@app.route('/api/rzeczy_znalezione/<id_ewidencyjny>', methods=['POST', 'PUT'])
def edit_item_endpoint(id_ewidencyjny):
    if not session.get('logged_in'):
        return jsonify({'message': 'unauthorized'}), 401
    form_data = request.get_json()
    try:
        item = LostItem(form_data, id_prefix=session.get('id_prefix'))
        item.id_ewidencyjny = id_ewidencyjny
        item.validate()
        if update_lost_item(item):
            return jsonify({"message": f"Item {id_ewidencyjny} updated successfully."}), 200
        else:
            return jsonify({"error": "Update failed (Item might not exist)."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/rzeczy_znalezione/<id_ewidencyjny>', methods=['GET'])
def get_item(id_ewidencyjny):
    if not session.get('logged_in'):
        return jsonify({'message': 'unauthorized'}), 401
    item = get_lost_item_by_id(id_ewidencyjny)
    if item is None:
        return jsonify({'message': 'not found'}), 404
    else:
        return jsonify(item), 201


@app.route('/api/narzedzia/auto_uzupelnianie', methods=['POST'])
def form_autocomplete():
    if 'photos' not in request.files:
        return jsonify({'error': "Nie znaleziono plików wejściowych"}), 400
    files_list = request.files.getlist('photos')
    if not files_list or files_list[0].filename == '':
        return jsonify({'error': 'Nie wybrano żadnych plików'}), 400

    images = [Image.open(file.stream) for file in files_list]
#    if PROCESSOR:
#        result = process_images(PROCESSOR, VLM, images)
#    else:
    result = mock_ai_metoda(files_list)
    return jsonify(result), 201


@app.route('/api/open-data/<powiat_slug>/xml')
def get_xml(powiat_slug):
    xml_content = generate_valid_xml(powiat_slug)
    response = make_response(xml_content)
    response.headers['Content-Type'] = 'application/xml; charset=utf-8'
    response.headers['Content-Disposition'] = 'inline; filename=harvester.xml'
    return response


@app.route('/api/open-data/<powiat_slug>/data.csv')
def get_csv_endpoint(powiat_slug):
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
    return response


def mock_ai_metoda(photos):
    return {'kategoria': 'pieniadze', 'opis': 'duzo pieniedzy'}


def run_app():
    global PROCESSOR, VLM
    print("--- Inicjalizacja Bazy Danych ---")
    create_office_accounts_table()
    create_lost_items_table()

    print('--- Przygotowywanie modeli AI ---')
    #if torch.cuda.is_available():
    #    PROCESSOR, VLM = get_vlm(VLM_PATH)
    #else:
    #    PROCESSOR, VLM = None, None
    print("--- Start Serwera Flask ---")
    app.run(debug=True, port=5000)
