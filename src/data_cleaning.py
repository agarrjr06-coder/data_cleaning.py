"""Limpeza e transformação de dados exportados de um CRM.

O script extrai informações de campos textuais, normaliza datas e gera
uma base final pronta para análise ou carga em banco de dados.
"""

from pathlib import Path
import re

import pandas as pd


INPUT_FILE = Path("data/input/crm.xlsx")
OUTPUT_FILE = Path("data/output/crm_clean.xlsx")


def extract_title_fields(title: object) -> list[str]:
    text = str(title).strip()

    date_match = re.search(r"^(\d{2}[/-]\d{2}[/-]\d{2,4})", text)
    emission_date = date_match.group(1) if date_match else ""

    value_match = re.search(r"(\d[\d.,]*,\d{2})$", text)
    invoice_value = value_match.group(1) if value_match else "0,00"

    nf_match = re.search(r"(?:N°\.:|NF:?)\s*([\d.]+)", text)
    if nf_match:
        raw_nf = nf_match.group(1).replace(".", "")
        invoice_number = str(int(raw_nf)) if raw_nf.isdigit() else raw_nf
    else:
        numbers = re.findall(r"\d{5,10}", text)
        invoice_number = str(int(numbers[0])) if numbers else "S/N"

    volume_match = re.search(r"(\d+)\s*(?:Volume|Vol)", text, re.IGNORECASE)
    volume = volume_match.group(1) if volume_match else "1"

    remainder = text
    if emission_date:
        remainder = remainder.replace(emission_date, "")
    if invoice_value:
        remainder = remainder.replace(invoice_value, "")

    junk_patterns = [
        r"(?i)N°\s*[:.]*",
        r"(?i)VALOR TOTAL DA NOTA",
        r"(?i)VALOR TOTAL",
        r"(?i)VALOR",
        r"(?i)Volumes?",
        r"(?i)NF:?",
        r"\bDA\b",
        r"\.\.",
        r"-",
        r"/",
        r"\.",
    ]

    for pattern in junk_patterns:
        remainder = re.sub(pattern, " ", remainder)

    remainder = re.sub(r"\d+", " ", remainder)
    brand = " ".join(remainder.split()).strip()

    return [emission_date, brand, invoice_number, volume, invoice_value]


def normalize_date(value: str) -> str:
    if not value:
        return "REVISAR"

    parsed = pd.to_datetime(value, dayfirst=True, errors="coerce")
    if pd.isna(parsed):
        return "REVISAR"

    return parsed.strftime("%d/%m/%Y %H:%M:%S")


def split_label(label: object) -> tuple[str, str]:
    text = str(label).upper()

    if "REPOSI" in text:
        process_type = "REPOSIÇÃO"
    elif "INCLU" in text:
        process_type = "INCLUSÃO"
    else:
        process_type = "CADASTRO"

    if process_type == "REPOSIÇÃO":
        responsible = "Yara"
    elif "NATHAN" in text:
        responsible = "Nathan"
    elif "DUDA" in text:
        responsible = "Duda"
    elif "DIEGO" in text:
        responsible = "Diego"
    else:
        responsible = "Outros"

    return process_type, responsible


def process_crm(input_file: Path = INPUT_FILE, output_file: Path = OUTPUT_FILE) -> None:
    if not input_file.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {input_file}")

    df = pd.read_excel(input_file)

    extracted = df["Title"].apply(extract_title_fields)
    df["Data Emissão Raw"] = [row[0] for row in extracted]
    df["Marca"] = [row[1] for row in extracted]
    df["N° NF"] = [row[2] for row in extracted]
    df["Volume"] = [row[3] for row in extracted]
    df["Valor NF"] = [row[4] for row in extracted]

    df["Data Emissão"] = df["Data Emissão Raw"].apply(normalize_date)
    df["Data finalização"] = pd.to_datetime(
        df["Due"], dayfirst=True, errors="coerce"
    ).dt.strftime("%d/%m/%Y %H:%M:%S")

    df[["Tipo NF", "Responsável"]] = df["Labels"].apply(
        lambda value: pd.Series(split_label(value))
    )

    final_columns = [
        "Data Emissão",
        "Marca",
        "N° NF",
        "Volume",
        "Valor NF",
        "Tipo NF",
        "Responsável",
        "Data finalização",
    ]

    output_file.parent.mkdir(parents=True, exist_ok=True)
    df[final_columns].to_excel(output_file, index=False)
    print("✅ SUCESSO! Arquivo processado e salvo.")
    print(f"📁 Destino: {output_file}")


if __name__ == "__main__":
    process_crm()
    
