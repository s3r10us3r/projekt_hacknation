import hashlib

CACHE = {
    "bf1fed44c11bbdcfb8ed66c6a6019ca3d71ad8b9cee3da028e2cca2ba43faab9": {"kategoria": "dokumenty_i_portfele", "opis": "Zgubiony przedmiot to czarny skórzany portfel. Ma gładką konsystencję i błyszczące wykończenie. Portfel jest zamykany, z klapką z drobnym, białym, przeszytym detalem. Portfel wygląda na wykonany z wysokiej jakości skóry, z profesjonalnym wykończeniem."},
    "59805ade0d4419909b167011103a75bce6df22ab8520e0e1df995ccde41f6175": {"kategoria": "inne", "opis": "Zgubiony przedmiot to czarny rower z czarnym siodełkiem, czarnymi kierownicami i czarnymi oponami. Ma czarną ramę i czarny koszyk z tyłu. Rower stoi na ścieżce ziemnej w lesie."}
}

def hash_file_storage(file_storage) -> str:
    h = hashlib.sha256()
    file_storage.stream.seek(0)
    while chunk := file_storage.stream.read(8192):
        h.update(chunk)
    file_storage.stream.seek(0)
    return h.hexdigest()
