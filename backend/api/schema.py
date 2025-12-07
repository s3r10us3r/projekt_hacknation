LOST_ITEM_SCHEMA = r'''
    {
  "title": "Rejestr Rzeczy Znalezionych",
  "type": "object",
  "properties": {
    "id_ewidencyjny": {
      "type": "string",
      "description": "Unikalny numer ewidencyjny nadany przez jednostkę samorządową (np. UM-WRO-2023-0001).",
      "pattern": "^([A-Z]{2,4}-[A-Z]{3,5}-\\d{4}-\\d{4})$",
      "maxLength": 30
    },
    "data_znalezienia": {
      "type": "string",
      "description": "Data znalezienia przedmiotu.",
      "format": "date"
    },
    "data_przekazania": {
      "type": "string",
      "description": "Data przekazania przedmiotu do Biura Rzeczy Znalezionych.",
      "format": "date"
    },
    "data_publikacji": {
      "type": "string",
      "description": "Data publikacji rekordu w portalu dane.gov.pl.",
      "format": "date-time"
    },
    "kategoria": {
      "type": "string",
      "description": "Kategoria przedmiotu (słownik zamknięty - Urzędnik wybiera z listy).",
      "enum": ["dokumenty_i_portfele", "elektronika", "odziez_i_akcesoria", "klucze", "bizuteria_i_zegarki", "pieniadze", "inne"],
      "maxLength": 30
    },
    "opis": {
      "type": "string",
      "description": "Szczegółowy opis przedmiotu (kolor, marka, stan).",
      "maxLength": 500
    },
    "powiat": {
      "type": "string",
      "description": "Nazwa powiatu, na którego terenie rzecz została znaleziona.",
      "maxLength": 50
    },
    "miejsce_znalezienia": {
      "type": "string",
      "description": "Ulica/miejsce, gdzie rzecz została znaleziona.",
      "maxLength": 100
    },
    "adres_odbioru": {
      "type": "string",
      "description": "Adres Biura Rzeczy Znalezionych (lub innej jednostki) przechowującego przedmiot.",
      "maxLength": 150
    },
    "email_kontaktowy": {
      "type": "string",
      "description": "Adres e-mail jednostki do kontaktu w sprawie odbioru.",
      "format": "email",
      "maxLength": 100
    },
    "telefon_kontaktowy": {
      "type": "string",
      "description": "Numer telefonu jednostki do kontaktu.",
      "pattern": "^\\+?[\\d\\s-]{9,15}$",
      "maxLength": 15
    },
    "status": {
      "type": "string",
      "description": "Status przedmiotu (słownik zamknięty).",
      "enum": ["do_odbioru", "odebrano"],
      "maxLength": 30
    }
  },
  "required": [
    "id_ewidencyjny",
    "data_znalezienia",
    "data_publikacji",
    "kategoria",
    "opis",
    "powiat",
    "adres_odbioru",
    "email_kontaktowy",
    "status"
  ],
  "additionalProperties": false
}
'''
