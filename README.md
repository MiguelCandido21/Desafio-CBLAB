# Desafio de Engenharia de Dados – Coco Bambu 2025

## Análise e Modelagem Relacional de Dados de ERP

Este repositório documenta a solução para o **Desafio 1** proposto pelo **CB-Lab**, focado na análise, modelagem e transformação de dados provenientes de um endpoint de ERP em um formato relacional otimizado para operações de restaurante. A solução foi desenvolvida com base em boas práticas de engenharia de dados, visando a criação de um pipeline de ETL robusto, reproduzível e pronto para produção.

---

### Sobre o Desafio

O desafio consiste em analisar um arquivo `ERP.json`, que representa a resposta de uma API de ERP para uma comanda de restaurante. A partir dele, foram solicitadas as seguintes entregas:

1. **Descrição do Esquema JSON**: Análise da estrutura hierárquica do arquivo.
2. **Transcrição para Tabelas SQL**: Conversão do JSON para um modelo relacional.
3. **Justificativa da Abordagem**: Detalhamento técnico das decisões tomadas.

---

### Análise do Esquema `ERP.json`

O arquivo `ERP.json` estrutura-se em um aninhamento que reflete a complexidade de uma operação de restaurante. A análise revelou as seguintes entidades principais:

* **Metadados da Requisição**: Contém informações sobre a data e hora da extração (`curUTC`) e a identificação da loja (`locRef`).
* **Comandas (`guestChecks`)**: É a entidade central, um array que armazena múltiplas comandas. Cada comanda agrega:
  * **Dados Operacionais**: Timestamps de abertura e fechamento, informações da mesa, número de clientes e identificação do funcionário.
  * **Valores Financeiros**: Subtotal, total, descontos e valores pagos.
  * **Impostos (`taxes`)**: Um array com os impostos aplicados.
  * **Itens da Comanda (`detailLines`)**: Um array que detalha cada item, podendo ser um item do menu, um desconto, uma taxa de serviço, um registro de pagamento ou um código de erro.

---

### Modelagem Relacional e Normalização

A transformação do JSON para um modelo relacional seguiu os princípios de normalização de dados para garantir a integridade, evitar redundância e otimizar a performance das consultas. A abordagem adotada foi a seguinte:

1. **Primeira Forma Normal (1FN)**: A estrutura aninhada do JSON foi decomposta, eliminando atributos multivalorados. As listas `guestChecks`, `taxes` e `detailLines` foram transformadas em tabelas distintas. Adicionalmente, as informações do funcionário (`employee`) na qual indica-se que adicione mais informações além do código, porém não foi recebido no arquivo JSON, originalmente aninhadas em `guestChecks`, foram extraídas para uma entidade própria, garantindo a atomicidade dos campos.
2. **Segunda Forma Normal (2FN)**: As dependências parciais foram resolvidas. A entidade `detailLine`, por exemplo, foi criada para garantir que cada item da comanda dependa integralmente de sua chave primária (`guestCheckLineItemId`).
3. **Terceira Forma Normal (3FN)**: As dependências transitivas foram eliminadas. Atributos que não dependiam diretamente da chave primária foram movidos para novas tabelas. Um exemplo é a separação dos subtipos de `detailLines` (`menuItem`, `discount`, `serviceCharge`, `tenderMedia` e `errorCode`), onde cada um armazena apenas os dados pertinentes ao seu contexto.

O modelo final é composto pelas seguintes entidades principais, utilizando `camelCase` para manter fidelidade à origem dos dados:

* `ErpMetadata`
* `employee`
* `guestChecks`
* `tax`
* `detailLine`
* `menuItem`
* `discount`
* `serviceCharge`
* `tenderMedia`
* `errorCode`

Este design assegura que as operações de `INSERT`, `UPDATE` e `DELETE` sejam realizadas de forma atômica e consistente.

➡️ Para uma descrição detalhada de cada tabela e atributo, consulte o arquivo **[`dicionario-de-dados.md`](./dicionario-de-dados.md)**.
➡️ O script de criação do banco de dados está disponível em **[`sql/schema.sql`](./sql/schema.sql)**.

---

### Implementação da Solução

A solução foi desenvolvida como um pipeline de ETL (Extração, Transformação e Carga) completo, containerizado com Docker para garantir a portabilidade e a facilidade de execução.

#### 1. Pipeline de ETL com Python (`etl.py`)

Um script em Python foi criado para orquestrar todo o processo:

* **Extração (Extract)**: O script lê o arquivo `ERP.json` local.
* **Transformação (Transform)**: Utilizando a biblioteca **Pandas**, o JSON aninhado é normalizado e transformado em múltiplos DataFrames, cada um correspondendo a uma tabela do modelo relacional.
* **Carga (Load)**: Com a biblioteca **SQLAlchemy**, o script se conecta ao banco de dados PostgreSQL e carrega os DataFrames nas tabelas correspondentes dentro do schema `sql-cblab`. O processo é envolto em uma única transação para garantir a atomicidade.

#### 2. Ambiente Containerizado com Docker

Para atender à recomendação de um código "confortável para colocar em produção", toda a solução foi containerizada:

* **`Dockerfile`**: Define a imagem da aplicação Python, instalando as dependências e o cliente do PostgreSQL.
* **`wait-for-it.sh`**: Um script shell robusto foi adicionado para garantir que o contêiner do ETL só inicie sua execução após o banco de dados estar totalmente pronto para aceitar conexões.
* **`docker-compose.yml`**: Orquestra a subida dos serviços. Ele define dois contêineres:
  1. `db`: O serviço do banco de dados **PostgreSQL 16**, com persistência de dados em um volume Docker.
  2. `etl`: O serviço da aplicação Python, que depende do `db` e executa o `wait-for-it.sh` seguido do `etl.py`.

---

### Como Executar o Projeto

Com o Docker e o Docker Compose instalados, a execução do projeto é simples e direta.

#### Pré-requisitos

* Docker
* Docker Compose

#### Passos para Execução

1. Clone este repositório para a sua máquina local.
2. Abra um terminal na raiz do projeto.
3. Execute o seguinte comando para construir as imagens e iniciar os contêineres:

   ```bash
   docker-compose up --build
   ```
4. O terminal exibirá os logs de ambos os serviços. O script `wait-for-it.sh` aguardará o banco de dados ficar pronto e, em seguida, o script `etl.py` será executado, carregando os dados.

Após a execução, os dados do `ERP.json` estarão persistidos no banco de dados PostgreSQL.

---

### Justificativa da Escolha da Tecnologia: PostgreSQL

A escolha do **PostgreSQL** foi fundamentada em pilares técnicos que o tornam ideal para este cenário:

* **Robustez e Confiabilidade**: Conformidade total com os padrões ACID, essencial para dados transacionais.
* **Suporte a Nomes Sensíveis ao Caso**: A capacidade do PostgreSQL de lidar com nomes de tabelas e colunas em `camelCase` (quando envoltos em aspas) foi crucial para manter a fidelidade 1:1 com os dados da API de origem.
* **Extensibilidade e Performance**: Recursos avançados de indexação e a capacidade de lidar com tipos de dados complexos como `JSONB` o tornam uma escolha escalável.
* **Ecossistema e Maturidade**: Vasta documentação, uma comunidade ativa e excelente compatibilidade com ferramentas de BI e ETL.

---

## Desafio 2: Arquitetura de Data Lake para Business Intelligence

### Introdução

O objetivo deste desafio é projetar a arquitetura de um Data Lake para armazenar as respostas de 5 APIs distintas. A solução deve ser escalável e resiliente, servindo como a fundação para as análises de Business Intelligence (BI) de toda a rede de restaurantes.

### 1. Por que armazenar as respostas das APIs?

Armazenar as respostas brutas das APIs, o **(raw data)**, é uma prática estratégica que transforma dados voláteis em um ativo corporativo permanente e confiável. Os principais motivos são:

* **Fonte da Verdade:** O `raw data` é a cópia fiel e imutável do dado na origem, garantindo consistência e uma base auditável para todas as análises.
* **Reprocessamento:** Permite que pipelines de dados sejam reexecutados para corrigir falhas ou aplicar novas regras de negócio, sem depender de APIs externas que podem se tornar indisponíveis.
* **Flexibilidade para o Futuro:** Preserva 100% da informação original, habilitando futuras análises de BI e projetos de Machine Learning que ainda não foram previstos.
* **Arquitetura Desacoplada:** Isola o processo de coleta (ingestão) do processo de consumo (análise), permitindo que as equipes trabalhem de forma independente e mais ágil.


> Desenvolvido por: **Miguel Candido**
```
