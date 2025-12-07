from api.db import get_all_lost_items
import io
import csv
import hashlib


def gen_lost_items_csv(powiat_slug):
    lost_items = get_all_lost_items(powiat=powiat_slug)
    field_names = [
        'id_ewidencyjny',
        'powiat',
        'data_znalezienia',
        'data_przekazania',
        'data_publikacji',
        'kategoria',
        'opis',
        'miejsce_znalezienia',
        'adres_odbioru',
        'email_kontaktowy',
        'telefon_kontaktowy',
        'status'
    ]

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=field_names, delimiter=';')
    writer.writeheader()
    for lost_item in lost_items:
        row_to_write = {k: lost_item[k] for k in field_names}
        writer.writerow(row_to_write)
    csv_content = output.getvalue()
    output.close()
    return csv_content, len(csv_content)


def get_md5(data_string):
    encoded_data = data_string.encode('utf-8')
    return hashlib.md5(encoded_data)


if __name__ == '__main__':
    csv_data = gen_lost_items_csv()
    print(csv_data)
    md5 = get_md5(csv_data)
    print(md5.hexdigest())
