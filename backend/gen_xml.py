import xml.etree.ElementTree as ET
from datetime import datetime

NS = "urn:otwarte-dane:harvester:1.13"


def generate_valid_xml(powiat_slug: str):
    powiat_name = powiat_slug.replace('-', ' ').title()
    dataset_id = f"rejestr-zgub-{powiat_slug}"
    url_csv = f"http://127.0.0.1/open-data/{powiat_slug}/data.csv"

    ET.register_namespace('od', NS)

    root = ET.Element(f"{{{NS}}}datasets")

    dataset = ET.SubElement(root, "dataset")
    dataset.set("status", "published")

    ET.SubElement(dataset, "extIdent").text = dataset_id[:36]

    title = ET.SubElement(dataset, "title")
    ET.SubElement(title, "polish").text = f"Rejestr Rzeczy Znalezionych - {powiat_name}"

    desc = ET.SubElement(dataset, "description")
    ET.SubElement(desc, "polish").text = "Publiczny wykaz rzeczy znalezionych prowadzony przez urząd."

    ET.SubElement(dataset, "url").text = "http://urzad.pl/bip/rzeczy-znalezione"
    ET.SubElement(dataset, "updateFrequency").text = "daily"

    cats = ET.SubElement(dataset, "categories")
    ET.SubElement(cats, "category").text = "GOVE"

    resources = ET.SubElement(dataset, "resources")
    res = ET.SubElement(resources, "resource")
    res.set("status", "published")

    ET.SubElement(res, "extIdent").text = f"res-{dataset_id}"[:36]
    ET.SubElement(res, "url").text = url_csv

    res_title = ET.SubElement(res, "title")
    ET.SubElement(res_title, "polish").text = "Wykaz Rzeczy (CSV)"

    res_desc = ET.SubElement(res, "description")
    ET.SubElement(res_desc, "polish").text = "Aktualny plik CSV z danymi."

    ET.SubElement(res, "availability").text = "remote"
    ET.SubElement(res, "dataDate").text = datetime.now().strftime("%Y-%m-%d")

    # --- Tagi ---
    tags = ET.SubElement(dataset, "tags")
    for tag_txt in ["rzeczy znalezione", "zguby", powiat_name]:
        tag = ET.SubElement(tags, "tag")
        tag.set("lang", "pl")
        tag.text = tag_txt

    return ET.tostring(root, encoding='utf-8', method='xml', xml_declaration=True)


if __name__ == '__main__':
    xml_bytes = generate_valid_xml('warszawa')
    import xml.dom.minidom
    dom = xml.dom.minidom.parseString(xml_bytes)
    pretty_xml = dom.toprettyxml(indent="    ")

    with open('dane_poprawione.xml', 'w', encoding='utf-8') as f:
        f.write(pretty_xml)
    print("✅ XML wygenerowany. Sprawdź plik dane_poprawione.xml")
