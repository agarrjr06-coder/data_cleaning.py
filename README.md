# Limpeza e Transformação de Dados de CRM

Projeto em Python para tratamento de dados exportados de CRM, com foco em transformar campos textuais pouco estruturados em uma base organizada para análise, indicadores ou carga posterior em banco de dados.

## Objetivo

Automatizar uma etapa que originalmente exigia leitura manual de títulos e etiquetas do CRM, extraindo informações operacionais e padronizando a saída.

## O que o script faz

- extrai data de emissão a partir de texto livre;
- identifica marca ou descrição principal;
- extrai número de nota fiscal;
- identifica volume;
- extrai valor informado no título;
- classifica o tipo de processo;
- identifica o responsável por regras configuráveis;
- normaliza datas;
- valida se as colunas esperadas existem;
- gera uma base final em Excel.

## Tecnologias

- Python
- Pandas
- OpenPyXL
- Regex

## Estrutura

```text
.
├── src/
│   └── data_cleaning.py
├── .gitignore
├── README.md
└── requirements.txt
```

As pastas `data/input/` e `data/output/` são utilizadas em tempo de execução e permanecem fora do versionamento para evitar publicação de bases locais.

## Entrada esperada

Por padrão, o script procura:

```text
data/input/crm.xlsx
```

O arquivo deve conter pelo menos as colunas:

- `Title`
- `Due`
- `Labels`

## Saída

O resultado é salvo por padrão em:

```text
data/output/crm_clean.xlsx
```

Com as colunas:

- Data Emissão
- Marca
- N° NF
- Volume
- Valor NF
- Tipo NF
- Responsável
- Data finalização

## Como executar

1. Instale as dependências:

```bash
pip install -r requirements.txt
```

2. Coloque o arquivo de entrada em `data/input/crm.xlsx`.

3. Execute:

```bash
python src/data_cleaning.py
```

## Sobre as regras

Este repositório é uma versão generalizada de uma automação criada a partir de uma necessidade operacional real. Os nomes e regras específicas foram substituídos por exemplos neutros para manter o projeto adequado a portfólio público.

A classificação de responsáveis fica concentrada em `RESPONSIBLE_RULES`, permitindo adaptação sem alterar a lógica principal do processamento.

## Limitações atuais

A extração depende do padrão textual presente em `Title`. Como campos livres podem variar, novos formatos podem exigir ajustes nas expressões regulares. O próximo passo natural seria incluir testes automatizados com diferentes formatos de entrada e uma pequena base sintética de exemplo.
