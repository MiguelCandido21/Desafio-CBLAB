# etl.py

import json
import pandas as pd
from sqlalchemy import create_engine
import time
import os

def extract_data(file_path):
    """Lê e carrega os dados do arquivo JSON."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def transform_data(data):
    """Transforma os dados JSON em DataFrames, mantendo os nomes de colunas originais."""
    all_guest_checks_raw = data.get('guestChecks', [])
    if not all_guest_checks_raw:
        print("Aviso: Nenhuma comanda ('guestChecks') encontrada no arquivo JSON.")
        return None

    # --- Camada de Normalização Bruta ---
    df_metadata = pd.DataFrame([{'curUTC': data['curUTC'], 'locRef': data['locRef']}])
    df_guest_checks_full = pd.json_normalize(all_guest_checks_raw)
    df_taxes_full = pd.json_normalize(all_guest_checks_raw, record_path=['taxes'], meta=['guestCheckId'], errors='ignore')
    df_detail_lines_full = pd.json_normalize(all_guest_checks_raw, record_path=['detailLines'], meta=['guestCheckId'], errors='ignore')

    # --- Preparação das Tabelas Finais (Mantendo Nomes Originais) ---
    df_ErpMetadata = df_metadata.reindex(columns=['curUTC', 'locRef'])
    df_employee = pd.DataFrame(df_guest_checks_full[['empNum']].drop_duplicates()) if 'empNum' in df_guest_checks_full else pd.DataFrame(columns=['empNum'])
    
    guest_checks_cols = [
        'guestCheckId', 'chkNum', 'opnBusDt', 'opnUTC', 'opnLcl', 'clsdBusDt', 'clsdUTC', 'clsdLcl',
        'lastTransUTC', 'lastTransLcl', 'lastUpdatedUTC', 'lastUpdatedLcl', 'clsdFlag', 'gstCnt',
        'subTtl', 'nonTxblSlsTtl', 'chkTtl', 'dscTtl', 'payTtl', 'balDueTtl', 'rvcNum', 'otNum',
        'ocNum', 'tblNum', 'tblName', 'empNum', 'numSrvcRd', 'numChkPrntd'
    ]
    df_guestChecks = df_guest_checks_full.reindex(columns=guest_checks_cols)
    df_guestChecks['curUTC'] = data['curUTC']

    df_tax = df_taxes_full.reindex(columns=['guestCheckId', 'taxNum', 'txblSlsTtl', 'taxCollTtl', 'taxRate', 'type'])
    
    detail_line_cols = [
        'guestCheckLineItemId', 'guestCheckId', 'rvcNum', 'dtlOtNum', 'dtlOcNum', 'lineNum', 'dtlId',
        'detailUTC', 'detailLcl', 'lastUpdateUTC', 'lastUpdateLcl', 'busDt', 'wsNum', 'dspTtl',
        'dspQty', 'aggTtl', 'aggQty', 'chkEmpId', 'chkEmpNum', 'svcRndNum', 'seatNum'
    ]
    df_detailLine = df_detail_lines_full.reindex(columns=detail_line_cols)

    def extract_sub_entity(df_full, entity_name, json_cols):
        entity_prefix = f'{entity_name}.'
        prefixed_cols = [f'{entity_prefix}{col}' for col in json_cols]
        if not any(c in df_full.columns for c in prefixed_cols):
            return pd.DataFrame()
        
        relevant_cols = ['guestCheckLineItemId'] + [col for col in prefixed_cols if col in df_full.columns]
        first_data_col = relevant_cols[1] if len(relevant_cols) > 1 else None
        if not first_data_col:
             return pd.DataFrame()

        df = df_full[relevant_cols].dropna(subset=[first_data_col]).copy()
        rename_map = {prefixed: original for prefixed, original in zip(prefixed_cols, json_cols)}
        df.rename(columns=rename_map, inplace=True)
        return df

    df_menuItem = extract_sub_entity(df_detail_lines_full, 'menuItem', ['miNum', 'modFlag', 'inclTax', 'activeTaxes', 'prcLvl'])
    df_discount = extract_sub_entity(df_detail_lines_full, 'discount', ['discountType', 'discountValue', 'isPercent'])
    df_serviceCharge = extract_sub_entity(df_detail_lines_full, 'serviceCharge', ['chargeName', 'chargeValue'])
    df_tenderMedia = extract_sub_entity(df_detail_lines_full, 'tenderMedia', ['mediaType', 'amount'])
    df_errorCode = extract_sub_entity(df_detail_lines_full, 'errorCode', ['code', 'message'])

    return {
        "ErpMetadata": df_ErpMetadata, "employee": df_employee, "guestChecks": df_guestChecks,
        "tax": df_tax, "detailLine": df_detailLine, "menuItem": df_menuItem,
        "discount": df_discount, "serviceCharge": df_serviceCharge, "tenderMedia": df_tenderMedia,
        "errorCode": df_errorCode
    }

def load_data(dataframes):
    if dataframes is None: return
    db_user, db_password, db_name, db_host = os.getenv("POSTGRES_USER"), os.getenv("POSTGRES_PASSWORD"), os.getenv("POSTGRES_DB"), os.getenv("DB_HOST", "db")
    db_schema = "sql-cblab"
    engine = create_engine(f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:5432/{db_name}")

    load_order = ["ErpMetadata", "employee", "guestChecks", "tax", "detailLine", "menuItem", "discount", "serviceCharge", "tenderMedia", "errorCode"]
    
    try:
        with engine.begin() as connection:
            print("Conexão e transação iniciadas.")
            for table_name in load_order:
                df = dataframes.get(table_name)
                # vvvv MUDANÇA PRINCIPAL AQUI vvvv
                if df is not None and not df.empty:
                    print(f"Carregando dados na tabela: {db_schema}.{table_name}...")
                    df.to_sql(table_name, connection, schema=db_schema, if_exists='append', index=False)
                    print(f"-> SUCESSO: {len(df)} linhas inseridas em {table_name}.")
                else:
                    # Log explícito para tabelas sem dados
                    print(f"Nenhum dado encontrado para a tabela {table_name}. Nenhuma linha inserida.")
            print("COMMIT realizado.")
    except Exception as e:
        print(f"Ocorreu um erro. ROLLBACK realizado. Erro: {e}")

if __name__ == "__main__":
    print("Iniciando pipeline de ETL...")
    raw_data = extract_data('data/ERP.json')
    transformed_data = transform_data(raw_data)
    load_data(transformed_data)
    print("Pipeline de ETL finalizada.")