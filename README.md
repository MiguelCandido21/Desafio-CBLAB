# Desafio de Engenharia de Dados – Coco Bambu 2025

## Análise e Modelagem Relacional de Dados de ERP

Este repositório documenta a solução para o **Desafio 1** proposto pelo **CB-Lab**, focado na análise, modelagem e transformação de dados provenientes de um endpoint de ERP em um formato relacional otimizado para operações de restaurante. A solução foi desenvolvida com base em boas práticas de engenharia de dados, visando escalabilidade, integridade e performance.

---

### Sobre o Desafio

O desafio consiste em analisar um arquivo `ERP.json`, que representa a resposta de uma API de ERP para uma comanda de restaurante. A partir dele, foram solicitadas as seguintes entregas:

1.  **Descrição do Esquema JSON**: Análise da estrutura hierárquica do arquivo.
2.  **Transcrição para Tabelas SQL**: Conversão do JSON para um modelo relacional.
3.  **Justificativa da Abordagem**: Detalhamento técnico das decisões tomadas.

---

### Análise do Esquema `ERP.json`

O arquivo `ERP.json` estrutura-se em um aninhamento que reflete a complexidade de uma operação de restaurante. A análise revelou as seguintes entidades principais:

* **Metadados da Requisição**: Contém informações sobre a data e hora da extração (`curUTC`) e a identificação da loja (`locRef`).
* **Comandas (`guestChecks`)**: É a entidade central, um array que armazena múltiplas comandas. Cada comanda agrega:
    * **Dados Operacionais**: Timestamps de abertura e fechamento, informações da mesa, número de clientes e identificação do funcionário.
    * **Valores Financeiros**: Subtotal, total, descontos e valores pagos.
    * **Impostos (`taxes`)**: Um array com os impostos aplicados, incluindo alíquota e valor.
    * **Itens da Comanda (`detailLines`)**: Um array que detalha cada item, podendo ser um item do menu, um desconto, uma taxa de serviço ou um registro de pagamento.

---

### Modelagem Relacional e Normalização

A transformação do JSON para um modelo relacional seguiu os princípios de normalização de dados para garantir a integridade, evitar redundância e otimizar a performance das consultas. A abordagem adotada foi a seguinte:

1.  **Primeira Forma Normal (1FN)**: A estrutura aninhada do JSON foi decomposta, eliminando atributos multivalorados. As listas `guestChecks`, `taxes` e `detailLines` foram transformadas em tabelas distintas. Adicionalmente, as informações do funcionário (`employee`), originalmente aninhadas em `guestChecks`, foram extraídas para uma entidade própria, garantindo a atomicidade dos campos.

2.  **Segunda Forma Normal (2FN)**: As dependências parciais foram resolvidas. A entidade `guest_check_detail_lines`, por exemplo, foi criada para garantir que cada item da comanda dependa integralmente de sua chave primária (`guest_check_line_item_id`) e não apenas de parte dela.

3.  **Terceira Forma Normal (3FN)**: As dependências transitivas foram eliminadas. Atributos que não dependiam diretamente da chave primária foram movidos para novas tabelas. Um exemplo é a separação dos subtipos de `detail_lines` (`menu_items`, `discounts`, `service_charges`, `tender_media` e `error_codes`), onde cada um armazena apenas os dados pertinentes ao seu contexto.

O modelo final é composto pelas seguintes entidades principais:

* `erp_metadata`
* `guest_checks`
* `employee`
* `guest_check_taxes`
* `guest_check_detail_lines`
* `menu_items`
* `discounts`
* `service_charges`
* `tender_media`
* `error_codes`

Este design assegura que as operações de `INSERT`, `UPDATE` e `DELETE` sejam realizadas de forma atômica e consistente, além de facilitar a criação de consultas analíticas complexas.

➡️ O **Modelo Conceitual (DER)** e o **script SQL** para a criação do banco de dados podem ser encontrados neste repositório.

---

### Justificativa da Escolha da Tecnologia: PostgreSQL

Para este desafio, a escolha do SGBD (Sistema de Gerenciamento de Banco de Dados) recaiu sobre o **PostgreSQL**. A decisão foi fundamentada nos seguintes pilares técnicos:

* **Robustez e Confiabilidade**: O PostgreSQL é conhecido por sua arquitetura robusta e conformidade com os padrões ACID (Atomicidade, Consistência, Isolamento e Durabilidade), o que é crucial para sistemas transacionais como os de um ERP de restaurante.
* **Suporte a Tipos de Dados Avançados**: O suporte nativo a `JSON` e `JSONB` é um diferencial estratégico. Ele permite armazenar o payload original da API de forma íntegra, facilitando a reingestão de dados e auditorias futuras, além de viabilizar consultas híbridas (relacionais e NoSQL) diretamente no banco.
* **Extensibilidade e Performance**: O PostgreSQL oferece recursos avançados de indexação (como GIN, para dados `JSONB`) e particionamento de tabelas, que são essenciais para otimizar a performance de consultas em grandes volumes de dados, como os gerados por uma cadeia de restaurantes.
* **Ecossistema e Maturidade**: Por ser um projeto open-source com décadas de desenvolvimento, o PostgreSQL possui uma comunidade ativa, vasta documentação e compatibilidade com as principais ferramentas de BI e ETL do mercado.

---

### Próximos Passos

* **Desenvolvimento da Pipeline de Ingestão**: Criar um script em Python para consumir o `ERP.json`, aplicar as transformações necessárias e popular o banco de dados PostgreSQL.
* **Armazenamento no Data Lake (Desafio 2)**: Projetar uma estrutura de pastas no Data Lake para armazenar as respostas da API, com controle de versionamento de schema para lidar com alterações como a renomeação de campos (`guestChecks.taxes` para `guestChecks.taxation`).
* **Conteinerização**: Utilizar Docker para criar um ambiente de desenvolvimento e produção reproduzível, facilitando o deploy da solução.

---

> Desenvolvido por: **Miguel Candido**
