import os
import json
from datetime import datetime, timedelta
import uuid
import random

# --- Configuração ---
# Lista dos 5 endpoints de API mencionados no desafio.
ENDPOINTS_API = [
    "getFiscalInvoice",
    "getGuestChecks",
    "getChargeBack",
    "getTransactions",
    "getCashManagementDetails"
]

# Lista de lojas para simular a ingestão.
LOJAS = ["101", "102", "103"]

# Diretório base para o nosso Data Lake local.
DATA_LAKE_BASE_DIR = "data_lake"

# --- Funções de Simulação de Dados ---

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
    
    # Simula a evolução do schema: algumas comandas usam 'taxes', outras 'taxation'
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
    """
    Simula a chamada de uma API e retorna um JSON de exemplo mais realista.
    No mundo real, esta função conteria a lógica para fazer uma requisição HTTP.
    """
    print(f"Simulando chamada para API '{api_name}' para a loja {store_id} na data {data_negocio}...")
    
    # Mapeia o nome da API para a função que gera os dados correspondentes
    geradores_de_dados = {
        "getFiscalInvoice": _gerar_dados_fiscais,
        "getGuestChecks": _gerar_comandas,
        "getChargeBack": _gerar_chargebacks,
        "getTransactions": _gerar_transacoes,
        "getCashManagementDetails": _gerar_detalhes_caixa
    }

    # Seleciona a função geradora correta
    funcao_geradora = geradores_de_dados.get(api_name)
    
    if not funcao_geradora:
        return None

    # Gera uma lista de dados, simulando que a API pode retornar múltiplos registros
    dados_gerados = [funcao_geradora(store_id, data_negocio) for _ in range(random.randint(5, 20))]

    # Monta a resposta final no padrão da API
    dados_mock = {
        "metadata": {
            "api_endpoint": api_name,
            "timestamp_request": datetime.now().isoformat(),
            "correlation_id": str(uuid.uuid4())
        },
        "payload": {
            "busDt": data_negocio,
            "storeId": store_id,
            "data": dados_gerados
        }
    }
    
    return dados_mock

def salvar_no_data_lake(api_name, data_negocio_dt, store_id, dados_json):
    """
    Salva os dados JSON na estrutura de pastas particionada do Data Lake.
    """
    # Extrai ano, mês e dia da data para criar as partições
    ano = data_negocio_dt.strftime("%Y")
    mes = data_negocio_dt.strftime("%m")
    dia = data_negocio_dt.strftime("%d")

    # Monta o caminho do diretório particionado
    caminho_particao = os.path.join(
        DATA_LAKE_BASE_DIR, "raw", api_name,
        f"ano={ano}", f"mes={mes}", f"dia={dia}", f"storeId={store_id}"
    )

    # Cria os diretórios se eles não existirem
    os.makedirs(caminho_particao, exist_ok=True)

    # Gera um nome de arquivo único usando timestamp e UUID
    timestamp_arquivo = datetime.now().strftime("%Y%m%d%H%M%S")
    id_unico = uuid.uuid4()
    nome_arquivo = f"{timestamp_arquivo}_{id_unico}.json"
    
    caminho_completo_arquivo = os.path.join(caminho_particao, nome_arquivo)

    # Salva o arquivo JSON
    try:
        with open(caminho_completo_arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados_json, f, ensure_ascii=False, indent=4)
        print(f"Dados salvos com sucesso em: {caminho_completo_arquivo}\n")
    except IOError as e:
        print(f"ERRO: Não foi possível salvar o arquivo {caminho_completo_arquivo}. Erro: {e}\n")

# --- Execução Principal ---

def main():
    """
    Função principal que orquestra o processo de ingestão.
    """
    print("--- Iniciando Pipeline de Ingestão para o Data Lake ---")
    
    # Usa a data de hoje como data de negócio para a simulação
    data_de_negocio_dt = datetime.now()
    data_de_negocio_str = data_de_negocio_dt.strftime("%Y-%m-%d")

    for loja_id in LOJAS:
        print(f"--- Processando dados para a Loja ID: {loja_id} ---")
        for endpoint in ENDPOINTS_API:
            # 1. Busca os dados (simulação)
            dados = simular_chamada_api(endpoint, data_de_negocio_str, loja_id)
            
            # 2. Salva no Data Lake
            if dados:
                salvar_no_data_lake(endpoint, data_de_negocio_dt, loja_id, dados)

    print("--- Processo de ingestão finalizado com sucesso. ---")

if __name__ == "__main__":
    main()
