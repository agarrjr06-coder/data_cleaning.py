# Limpeza de Dados de CRM

Script em Python para limpeza e transformação de dados exportados de um CRM.

## Objetivo

Automatizar o tratamento de uma base bruta de CRM, extraindo e
padronizando informações necessárias para análise de dados.

## O que o script faz

- Extrai informações do campo `Title`
- Identifica a data de emissão
- Identifica a marca
- Extrai o número da nota fiscal
- Extrai volume e valor da nota
- Classifica o tipo de processo
- Identifica o responsável
- Normaliza datas
- Gera uma base final em Excel

## Tecnologias

- Python
- Pandas
- OpenPyXL
- Expressões regulares (Regex)

## Estrutura do projeto

    data_cleaning.py/
    ├── src/
    │   └── data_cleaning.py
    ├── .gitignore
    ├── README.md
    └── requirements.txt

## Como executar

1. Instale as dependências:

       pip install -r requirements.txt

2. Coloque o arquivo de entrada em:

       data/input/crm.xlsx

3. Execute:

       python src/data_cleaning.py

4. O arquivo tratado será gerado em:

       data/output/crm_clean.xlsx
