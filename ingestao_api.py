import os
import json
from datetime import datetime, timedelta
import uuid
import random
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

ENDPOINTS_API = [
    "getFiscalInvoice",
    "getGuestChecks",
    "getChargeBack",
    "getTransactions",
    "getCashManagementDetails"
]
LOJAS = ["101", "102", "103"]

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
DATA_LAKE_BUCKET = os.getenv("DATA_LAKE_BUCKET")
AWS_REGION = "us-east-1"

def inicializar_s3_client():
    """Inicializa e retorna o cliente S3 (boto3) para o MinIO."""
    try:
        client = boto3.client(
            's3',
            endpoint_url=f"http://{MINIO_ENDPOINT}",
            aws_access_key_id=MINIO_ACCESS_KEY,
            aws_secret_access_key=MINIO_SECRET_KEY,
            region_name=AWS_REGION
        )
        client.list_buckets()
        print("Conexão com o MinIO (via Boto3) estabelecida com sucesso.")
        return client
    except Exception as e:
        print(f"Erro ao conectar com o MinIO (via Boto3): {e}")
        return None

def garantir_criacao_bucket(client, bucket_name: str):
    """Verifica se um bucket existe e o cria caso não exista, usando boto3."""
    if not client:
        print("Cliente S3 não inicializado. Impossível criar o bucket.")
        return
    try:
        client.head_bucket(Bucket=bucket_name)
        print(f"Bucket '{bucket_name}' já existe.")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            print(f"Bucket '{bucket_name}' não encontrado. Criando...")
            try:
                client.create_bucket(Bucket=bucket_name)
                print(f"Bucket '{bucket_name}' criado com sucesso.")
            except ClientError as creation_error:
                print(f"Erro ao criar o bucket: {creation_error}")
        else:
            print(f"Erro ao verificar o bucket: {e}")


def _gerar_dados_fiscais(store_id, data_negocio):
    """Gera um exemplo de nota fiscal."""
    return {
        "invoiceId": str(uuid.uuid4()),
        "totalAmount": round(random.uniform(50.0, 500.0), 2),
        "issueDate": data_negocio,
        "storeId": store_id
    }

def _gerar_comandas(store_id, data_negocio):
    """Gera um exemplo de comanda com itens."""
    itens = []
    for _ in range(random.randint(1, 5)):
        itens.append({
            "menuItemId": random.randint(1000, 2000),
            "description": random.choice(["Prato Principal", "Bebida", "Sobremesa"]),
            "quantity": random.randint(1, 3),
            "price": round(random.uniform(15.0, 120.0), 2)
        })
    comanda = {
        "guestCheckId": str(uuid.uuid4()),
        "storeId": store_id,
        "busDt": data_negocio,
        "detailLines": itens,
        "total": sum(item['price'] * item['quantity'] for item in itens)
    }
    if int(store_id) % 2 == 0:
        comanda["taxes"] = round(comanda["total"] * 0.1, 2)
    else:
        comanda["taxation"] = round(comanda["total"] * 0.1, 2)
    return comanda

def _gerar_chargebacks(store_id, data_negocio):
    """Gera um exemplo de chargeback."""
    return {
        "chargeBackId": str(uuid.uuid4()),
        "transactionId": str(uuid.uuid4()),
        "reason": random.choice(["Fraude", "Produto não entregue", "Erro de processamento"]),
        "amount": round(random.uniform(20.0, 300.0), 2),
        "date": data_negocio,
        "storeId": store_id
    }

def _gerar_transacoes(store_id, data_negocio):
    """Gera um exemplo de transação financeira."""
    return {
        "transactionId": str(uuid.uuid4()),
        "media": random.choice(["Cartão de Crédito", "Cartão de Débito", "PIX"]),
        "amount": round(random.uniform(10.0, 1000.0), 2),
        "timestamp": (datetime.now() - timedelta(minutes=random.randint(1, 60))).isoformat(),
        "storeId": store_id
    }

def _gerar_detalhes_caixa(store_id, data_negocio):
    """Gera um exemplo de detalhes de gerenciamento de caixa."""
    return {
        "cashManagementId": str(uuid.uuid4()),
        "openingBalance": round(random.uniform(500.0, 1500.0), 2),
        "closingBalance": round(random.uniform(2000.0, 5000.0), 2),
        "date": data_negocio,
        "storeId": store_id
    }

def simular_chamada_api(api_name, data_negocio, store_id):
    """Simula a chamada de uma API e retorna um JSON de exemplo."""
    print(f"Simulando chamada para API '{api_name}' para a loja {store_id} na data {data_negocio}...")
    geradores_de_dados = {
        "getFiscalInvoice": _gerar_dados_fiscais,
        "getGuestChecks": _gerar_comandas,
        "getChargeBack": _gerar_chargebacks,
        "getTransactions": _gerar_transacoes,
        "getCashManagementDetails": _gerar_detalhes_caixa
    }
    funcao_geradora = geradores_de_dados.get(api_name)
    if not funcao_geradora:
        return None
    dados_gerados = [funcao_geradora(store_id, data_negocio) for _ in range(random.randint(5, 20))]
    return {
        "metadata": { "api_endpoint": api_name, "timestamp_request": datetime.now().isoformat(), "correlation_id": str(uuid.uuid4()) },
        "payload": { "busDt": data_negocio, "storeId": store_id, "data": dados_gerados }
    }


def salvar_no_data_lake(client, api_name, data_negocio_dt, store_id, dados_json, correlation_id):
    """Salva os dados JSON no MinIO usando um nome de arquivo robusto e informativo."""
    if not client:
        print("ERRO: Cliente S3 não inicializado. Abortando upload.")
        return

    ano = data_negocio_dt.strftime("%Y")
    mes = data_negocio_dt.strftime("%m")
    dia = data_negocio_dt.strftime("%d")

    caminho_particao = os.path.join(
        api_name, f"ano={ano}", f"mes={mes}", f"dia={dia}", f"storeId={store_id}"
    )
    
    timestamp_arquivo = datetime.now().strftime("%Y%m%d%H%M%S%f")
    nome_arquivo = f"{timestamp_arquivo}_{store_id}_{correlation_id}.json"
    
    caminho_completo_objeto = os.path.join(caminho_particao, nome_arquivo)

    json_bytes = json.dumps(dados_json, ensure_ascii=False, indent=4).encode('utf-8')

    try:
        client.put_object(
            Bucket=DATA_LAKE_BUCKET,
            Key=caminho_completo_objeto,
            Body=json_bytes,
            ContentType='application/json'
        )
        print(f"Dados salvos com sucesso em: s3://{DATA_LAKE_BUCKET}/{caminho_completo_objeto}\n")
    except ClientError as e:
        print(f"ERRO: Não foi possível salvar o objeto no MinIO. Erro: {e}\n")


def main():
    """Função principal que orquestra o processo de ingestão."""
    s3_client = inicializar_s3_client()
    
    garantir_criacao_bucket(s3_client, DATA_LAKE_BUCKET)
    
    print("\n--- Iniciando Pipeline de Ingestão para o Data Lake (MinIO com Boto3) ---")
    data_de_negocio_dt = datetime.now()
    data_de_negocio_str = data_de_negocio_dt.strftime("%Y-%m-%d")

    for loja_id in LOJAS:
        print(f"--- Processando dados para a Loja ID: {loja_id} ---")
        for endpoint in ENDPOINTS_API:
            dados = simular_chamada_api(endpoint, data_de_negocio_str, loja_id)
            if dados:
                correlation_id = dados['metadata']['correlation_id']
                salvar_no_data_lake(s3_client, endpoint, data_de_negocio_dt, loja_id, dados, correlation_id)

    print("--- Processo de ingestão finalizado com sucesso. ---")


if __name__ == "__main__":
    main()