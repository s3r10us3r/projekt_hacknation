from api.db import get_all_lost_items, get_all_datasets, insert_ds
from datetime import date
import io
import csv
import hashlib


def gen_lost_items_csv(powiat_slug, date_str=str(str(date.today()))):
    datasets = get_all_datasets(powiat_slug)
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
    has_dup = False
    md5 = get_md5(csv_content)
    if datasets:
        for dataset in datasets:
            if dataset['md5'] == md5:
                has_dup = True
                break
    if not has_dup:
        insert_ds(md5, csv_content, date_str, powiat_slug)





def get_md5(data_string):
    encoded_data = data_string.encode('utf-8')
    return hashlib.md5(encoded_data).hexdigest()


if __name__ == '__main__':
    import sys
    gen_lost_items_csv(sys.argv[1])
