"""Limpeza e transformação de dados exportados de um CRM.

O script extrai informações de campos textuais, normaliza datas e gera
uma base final pronta para análise ou carga em banco de dados.

Os nomes e regras abaixo foram generalizados para uso demonstrativo em
portfólio. Ajuste os mapeamentos conforme a realidade de cada operação.
"""

from pathlib import Path
import re

import pandas as pd


INPUT_FILE = Path("data/input/crm.xlsx")
OUTPUT_FILE = Path("data/output/crm_clean.xlsx")

RESPONSIBLE_RULES = {
    "ANALISTA A": ["ANALISTA A", "RESPONSAVEL A"],
    "ANALISTA B": ["ANALISTA B", "RESPONSAVEL B"],
    "ANALISTA C": ["ANALISTA C", "RESPONSAVEL C"],
}


def extract_title_fields(title: object) -> list[str]:
    text = "" if pd.isna(title) else str(title).strip()

    date_match = re.search(r"^(\d{2}[/-]\d{2}[/-]\d{2,4})", text)
    emission_date = date_match.group(1) if date_match else ""

    value_match = re.search(r"(\d[\d.,]*,\d{2})$", text)
    invoice_value = value_match.group(1) if value_match else "0,00"

    nf_match = re.search(r"(?:N[°º]?\.?|NF)\s*[:.-]?\s*([\d.]+)", text, re.IGNORECASE)
    if nf_match:
        raw_nf = nf_match.group(1).replace(".", "")
        invoice_number = raw_nf.lstrip("0") or "0"
    else:
        numbers = re.findall(r"\b\d{5,10}\b", text)
        invoice_number = numbers[0].lstrip("0") if numbers else "S/N"

    volume_match = re.search(r"(\d+)\s*(?:Volumes?|Vol)\b", text, re.IGNORECASE)
    volume = volume_match.group(1) if volume_match else "1"

    remainder = text
    if emission_date:
        remainder = remainder.replace(emission_date, " ")
    if value_match:
        remainder = remainder[: value_match.start()]

    junk_patterns = [
        r"(?i)N[°º]?\s*[:.\-]*",
        r"(?i)VALOR TOTAL DA NOTA",
        r"(?i)VALOR TOTAL",
        r"(?i)VALOR",
        r"(?i)Volumes?",
        r"(?i)NF\s*:?",
        r"\bDA\b",
        r"[\-/]+",
        r"\.{2,}",
    ]

    for pattern in junk_patterns:
        remainder = re.sub(pattern, " ", remainder)

    remainder = re.sub(r"\b\d+\b", " ", remainder)
    brand = " ".join(remainder.split()).strip()

    return [emission_date, brand, invoice_number, volume, invoice_value]


def normalize_date(value: object) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "REVISAR"

    parsed = pd.to_datetime(value, dayfirst=True, errors="coerce")
    if pd.isna(parsed):
        return "REVISAR"

    return parsed.strftime("%d/%m/%Y %H:%M:%S")


def identify_process_type(label: object) -> str:
    text = "" if pd.isna(label) else str(label).upper()

    if "REPOSI" in text:
        return "REPOSIÇÃO"
    if "INCLU" in text:
        return "INCLUSÃO"
    return "CADASTRO"


def identify_responsible(label: object) -> str:
    text = "" if pd.isna(label) else str(label).upper()

    for responsible, aliases in RESPONSIBLE_RULES.items():
        if any(alias in text for alias in aliases):
            return responsible

    return "OUTROS"


def validate_columns(df: pd.DataFrame, required_columns: list[str]) -> None:
    missing = [column for column in required_columns if column not in df.columns]
    if missing:
        raise ValueError(
            "Colunas obrigatórias ausentes no arquivo de entrada: " + ", ".join(missing)
        )


def process_crm(input_file: Path = INPUT_FILE, output_file: Path = OUTPUT_FILE) -> None:
    if not input_file.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {input_file}")

    df = pd.read_excel(input_file)
    validate_columns(df, ["Title", "Due", "Labels"])

    extracted = df["Title"].apply(extract_title_fields)
    df["Data Emissão Raw"] = [row[0] for row in extracted]
    df["Marca"] = [row[1] for row in extracted]
    df["N° NF"] = [row[2] for row in extracted]
    df["Volume"] = pd.to_numeric([row[3] for row in extracted], errors="coerce").fillna(1).astype(int)
    df["Valor NF"] = [row[4] for row in extracted]

    df["Data Emissão"] = df["Data Emissão Raw"].apply(normalize_date)
    df["Data finalização"] = df["Due"].apply(normalize_date)
    df["Tipo NF"] = df["Labels"].apply(identify_process_type)
    df["Responsável"] = df["Labels"].apply(identify_responsible)

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

    print("✅ Arquivo processado com sucesso.")
    print(f"📁 Destino: {output_file}")


if __name__ == "__main__":
    process_crm()
