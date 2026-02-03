# data_cleaning.py
"""
CRM raw data is messy, inconsistent, and full of junk rows/empty columns - Automated Python script using Pandas to standardize dates, clean strings, and handle null values, preparing data for SQL injection or Power BI -  Reduced data preparation time by [X]% and eliminated manual entry errors
"""

import pandas as pd
import numpy as np
import os
import re

# --- CONFIGURAÇÕES DE CAMINHO ---
ARQUIVO_ORIGEM = r"C:abc\CProjetos_BI\crm_28_01_26.xlsx"
ARQUIVO_DESTINO = r"C:abc\CProjetos_BI\crm_limpeza_final1.xlsx"

def processar_crm_perfeito():
    try:
        if not os.path.exists(ARQUIVO_ORIGEM):
            print(f"❌ ERRO: Arquivo não encontrado.")
            return

        df = pd.read_excel(ARQUIVO_ORIGEM)

        def extrair_por_hierarquia(titulo):
            t = str(titulo).strip()
            
            # 1. DATA DE EMISSÃO (Primeiro dado da linha)
            # Aceita datas com 2, 3 ou 4 dígitos no ano para capturar erros do CRM
            data_match = re.search(r'^(\d{2}[/-]\d{2}[/-]\d{2,4})', t)
            data_emi = data_match.group(1) if data_match else ""
            
            # 2. VALOR (Sempre no final da linha)
            valor_match = re.search(r'(\d[\d.,]*,\d{2})$', t)
            valor_val = valor_match.group(1) if valor_match else "0,00"
            
            # 3. NF (Remove pontos e mata os zeros à esquerda)
            nf_match = re.search(r'(?:N°\.:|NF:?)\s*([\d.]+)', t)
            if nf_match:
                nf_raw = nf_match.group(1).replace('.', '')
                nf_final = str(int(nf_raw)) if nf_raw.isdigit() else nf_raw
            else:
                nums = re.findall(r'\d{5,10}', t)
                nf_final = str(int(nums[0])) if nums else "S/N"
                
            # 4. VOLUME
            vol_match = re.search(r'(\d+)\s*(?:Volume|Vol)', t, re.IGNORECASE)
            vol_val = vol_match.group(1) if vol_match else "1"

            # 5. MARCA (Limpando o que sobrou no meio)
            sobra = t
            if data_emi: sobra = sobra.replace(data_emi, "")
            if valor_val: sobra = sobra.replace(valor_val, "")
            
            termos_lixo = [
                r'(?i)N°\s*[:.]*', r'(?i)VALOR TOTAL DA NOTA', r'(?i)VALOR TOTAL', 
                r'(?i)VALOR', r'(?i)Volumes?', r'(?i)NF:?', r'\bDA\b', r'\.\.', r'-', r'/', r'\.'
            ]
            for termo in termos_lixo:
                sobra = re.sub(termo, ' ', sobra)
            
            sobra = re.sub(r'\d+', ' ', sobra) # Remove números residuais da marca
            marca_limpa = " ".join(sobra.split()).strip()

            return [data_emi, marca_limpa, nf_final, vol_val, valor_val]

        print("🔄 Processando títulos e corrigindo datas malformadas...")
        extraidos = df['Title'].apply(extrair_por_hierarquia)
        
        df['Data Emissão Raw'] = [d[0] for d in extraidos]
        df['Marca']            = [d[1] for d in extraidos]
        df['N° NF']            = [d[2] for d in extraidos]
        df['Volume']           = [d[3] for d in extraidos]
        df['Valor NF']         = [d[4] for d in extraidos]

        # --- LÓGICA DE RECUPERAÇÃO DE DATA (Resolve o problema do "REVISAR") ---
        def corrigir_data(data_str):
            if not data_str: return "REVISAR"
            
            # Tenta conversão direta (para anos com 4 dígitos)
            dt = pd.to_datetime(data_str, dayfirst=True, errors='coerce')
            
            if pd.isna(dt):
                # Se falhar (ex: 31/12/202), pegamos dia e mês e forçamos 2025/2026
                partes = re.findall(r'\d+', data_str)
                if len(partes) >= 2:
                    return f"{partes[0].zfill(2)}/{partes[1].zfill(2)}/2025 00:00:00"
                return "REVISAR"
            
            return dt.strftime('%d/%m/%Y %H:%M:%S')

        df['Data Emissão'] = df['Data Emissão Raw'].apply(corrigir_data)

        # Coluna E: Data Finalização
        df['Data finalização'] = pd.to_datetime(df['Due'], dayfirst=True, errors='coerce').dt.strftime('%d/%m/%Y %H:%M:%S')

        # Coluna G: Divisão de Responsável e Tipo
        def separar_coluna_g(label):
            l = str(label).upper()
            tipo = 'REPOSIÇÃO' if 'REPOSI' in l else ('INCLUSÃO' if 'INCLU' in l else 'CADASTRO')
            if tipo == 'REPOSIÇÃO': resp = 'Yara'
            elif 'NATHAN' in l: resp = 'Nathan'
            elif 'DUDA' in l: resp = 'Duda'
            elif 'DIEGO' in l: resp = 'Diego'
            else: resp = 'Outros'
            return tipo, resp

        df[['Tipo NF', 'Responsável']] = df['Labels'].apply(lambda x: pd.Series(separar_coluna_g(x)))

        colunas_finais = ['Data Emissão', 'Marca', 'N° NF', 'Volume', 'Valor NF', 'Tipo NF', 'Responsável', 'Data finalização']

        try:
            df[colunas_finais].to_excel(ARQUIVO_DESTINO, index=False)
            print("✅ SUCESSO! Datas corrigidas e zeros removidos da NF.")
            os.startfile(os.path.dirname(ARQUIVO_DESTINO))
        except PermissionError:
            print("❌ ERRO: O Excel está aberto. Feche-o e rode o script novamente.")

    except Exception as e:
        print(f"❌ Erro Crítico: {e}")

if __name__ == "__main__":
    processar_crm_perfeito()
