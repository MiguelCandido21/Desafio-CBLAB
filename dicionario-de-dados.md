# Dicionário de Dados - ERP Restaurante

Este documento serve como um guia de referência detalhado para o modelo de dados relacional projetado a partir do `ERP.json`. Cada seção descreve uma entidade (tabela), seu propósito no sistema, e os atributos que a compõem.

A coluna **"Nome de Campo Sugerido"** apresenta uma nomenclatura ideal, seguindo as melhores práticas de clareza e padronização **(snake_case)**. Embora os nomes originais sejam mantidos no Data Lake para garantir a conformidade com a origem, esta coluna serve como uma referência para uma modelagem de boas práticas.

---

## 🗃️ Entidades do Modelo

### 🏢 `erp_metadata`

Armazena os metadados de cada extração de dados da API. Esta tabela é fundamental para o rastreamento e a auditoria dos dados.

| Campo Original (API) | Nome de Campo Sugerido       | Tipo      | Descrição Detalhada                                                                                                  |
| -------------------- | ---------------------------- | --------- | ---------------------------------------------------------------------------------------------------------------------- |
| `cur_utc`          | `extraction_utc_timestamp` | TIMESTAMP | **Chave Primária.** Timestamp da execução da API, servindo como um identificador único para o lote de dados. |
| `loc_ref`          | `location_reference_id`    | VARCHAR   | Referência da loja ou unidade de negócio de onde os dados foram extraídos.                                          |

---

### 🧾 `guest_checks` (Comandas)

Tabela central do modelo, representando cada transação ou "comanda" individual.

| Campo Original (API) | Nome de Campo Sugerido      | Tipo      | Descrição Detalhada                                                                         |
| -------------------- | --------------------------- | --------- | --------------------------------------------------------------------------------------------- |
| `guestCheckId`     | `guest_check_id`          | BIGINT    | **Chave Primária.** Identificador único global da comanda no sistema de origem (ERP). |
| `chkNum`           | `check_number`            | INT       | Número sequencial da comanda, geralmente visível para o cliente e para a operação.        |
| `opnBusDt`         | `opening_business_date`   | DATE      | Data comercial de abertura da comanda, usada para relatórios financeiros diários.           |
| `opnUTC`           | `opening_utc_timestamp`   | TIMESTAMP | Timestamp exato da abertura da comanda em Coordinated Universal Time (UTC).                   |
| `opnLcl`           | `opening_local_timestamp` | TIMESTAMP | Timestamp da abertura no fuso horário local da loja.                                         |
| `clsdBusDt`        | `closing_business_date`   | DATE      | Data comercial de fechamento, importante para o fechamento de caixa.                          |
| `clsdUTC`          | `closing_utc_timestamp`   | TIMESTAMP | Timestamp exato do fechamento da comanda em UTC.                                              |
| `clsdLcl`          | `closing_local_timestamp` | TIMESTAMP | Timestamp do fechamento no fuso horário local.                                               |
| `lastTransUTC`     | `last_transaction_utc`    | TIMESTAMP | Registra a última transação (pagamento, item adicionado) na comanda em UTC.                |
| `lastUpdatedUTC`   | `last_updated_utc`        | TIMESTAMP | Data da última atualização de qualquer campo da comanda em UTC.                            |
| `clsdFlag`         | `is_closed_flag`          | BOOLEAN   | Booleano que indica se a comanda foi finalizada e fechada.`True` para fechada.              |
| `gstCnt`           | `guest_count`             | INT       | Quantidade de clientes (convidados) atendidos na comanda.                                     |
| `subTtl`           | `subtotal`                | DECIMAL   | Valor total dos itens antes de impostos e descontos.                                          |
| `nonTxblSlsTtl`    | `non_taxable_sales_total` | DECIMAL   | Total de vendas não tributáveis, como gorjetas opcionais.                                   |
| `chkTtl`           | `check_total`             | DECIMAL   | Valor final da comanda (`sub_ttl` + `taxes` - `discounts`).                             |
| `dscTtl`           | `discount_total`          | DECIMAL   | Soma total dos descontos aplicados.                                                           |
| `payTtl`           | `payment_total`           | DECIMAL   | Valor total efetivamente pago pelo cliente.                                                   |
| `balDueTtl`        | `balance_due_total`       | DECIMAL   | Saldo residual a ser pago. Geralmente nulo se `pay_ttl` >= `chk_ttl`.                     |
| `rvcNum`           | `revenue_center_number`   | INT       | Identificador do centro de receita (ex: 101 para Salão, 102 para Delivery).                  |
| `tblNum`           | `table_number`            | INT       | Número da mesa onde o atendimento foi realizado.                                             |
| `tblName`          | `table_name`              | VARCHAR   | Nome ou descrição da mesa (ex: "Varanda 05").                                               |
| `empNum`           | `employee_number`         | INT       | **Chave Estrangeira** para a tabela `employee`.                                       |
| `numSrvcRd`        | `service_round_count`     | INT       | Número de "rodadas de serviço", útil para medir a frequência de atendimento.              |
| `numChkPrntd`      | `check_printed_count`     | INT       | Quantidade de vezes que a conta foi impressa.                                                 |

---

### 👤 `employee` (Funcionários)

Entidade dedicada a armazenar informações sobre os funcionários.

| Campo Original (API)   | Nome de Campo Sugerido | Tipo    | Descrição Detalhada                                      |
| ---------------------- | ---------------------- | ------- | ---------------------------------------------------------- |
| `empNum`             | `employee_number`    | INT     | **Chave Primária.** ID único do funcionário.      |
| `(não disponível)` | `employee_name`      | VARCHAR | Nome do funcionário (campo sugerido para enriquecimento). |
| `(não disponível)` | `employee_role`      | VARCHAR | Cargo ou função (campo sugerido para enriquecimento).    |

---

### 💸 `guest_check_taxes` (Impostos da Comanda)

Detalha todos os impostos incidentes sobre uma comanda.

| Campo Original (API) | Nome de Campo Sugerido  | Tipo    | Descrição Detalhada                                          |
| -------------------- | ----------------------- | ------- | -------------------------------------------------------------- |
| `(gerado)`         | `tax_record_id`       | SERIAL  | **Chave Primária.** Identificador sequencial único.    |
| `guestCheckId`     | `guest_check_id`      | BIGINT  | **Chave Estrangeira** para `guest_checks`.             |
| `taxNum`           | `tax_number`          | INT     | Código de identificação do tipo de imposto (ex: ISS, ICMS). |
| `txblSlsTtl`       | `taxable_sales_total` | DECIMAL | Base de cálculo sobre a qual o imposto foi aplicado.          |
| `taxCollTtl`       | `tax_collected_total` | DECIMAL | Valor monetário do imposto recolhido.                         |
| `taxRate`          | `tax_rate_percentage` | DECIMAL | Percentual da alíquota do imposto.                            |
| `type`             | `tax_type`            | INT     | Categoria ou tipo fiscal do imposto.                           |

---

### 🧾 `guest_check_detail_lines` (Itens da Comanda)

Registra cada linha de item dentro de uma comanda.

| Campo Original (API)     | Nome de Campo Sugerido    | Tipo      | Descrição Detalhada                                                |
| ------------------------ | ------------------------- | --------- | -------------------------------------------------------------------- |
| `guestCheckLineItemId` | `line_item_id`          | BIGINT    | **Chave Primária.** ID único global para a linha de detalhe. |
| `guestCheckId`         | `guest_check_id`        | BIGINT    | **Chave Estrangeira** para `guest_checks`.                   |
| `lineNum`              | `line_number`           | INT       | Posição sequencial do item na comanda.                             |
| `detailUTC`            | `detail_utc_timestamp`  | TIMESTAMP | Timestamp UTC exato em que o item foi adicionado.                    |
| `aggTtl`               | `aggregate_total`       | DECIMAL   | Valor total agregado para o item (`dsp_ttl` * `dsp_qty`).        |
| `aggQty`               | `aggregate_quantity`    | INT       | Quantidade total agregada do item.                                   |
| `chkEmpId`             | `check_employee_id`     | BIGINT    | ID do funcionário que registrou o item.                             |
| `chkEmpNum`            | `check_employee_number` | INT       | Número do funcionário que registrou o item.                        |
| `svcRndNum`            | `service_round_number`  | INT       | Rodada de serviço em que o item foi solicitado.                     |
| `seatNum`              | `seat_number`           | INT       | Número do assento do cliente que solicitou o item.                  |

---

### 🧩 Subentidades de `detail_lines`

Tabelas que especializam os registros de `guest_check_detail_lines`.

#### 🍔 `menu_items`

| Campo Original (API)     | Nome de Campo Sugerido | Tipo    | Descrição Detalhada                               |
| ------------------------ | ---------------------- | ------- | --------------------------------------------------- |
| `guestCheckLineItemId` | `line_item_id`       | BIGINT  | **Chave Primária e Estrangeira**.            |
| `miNum`                | `menu_item_number`   | INT     | Código de identificação do produto no cardápio. |
| `modFlag`              | `is_modified_flag`   | BOOLEAN | Indica se o item sofreu alguma modificação.       |
| `inclTax`              | `included_tax`       | DECIMAL | Valor do imposto já embutido no preço do item.    |
| `prcLvl`               | `price_level`        | INT     | Nível de preço aplicado (ex: happy hour).         |

#### 🎟️ `discounts`

| Campo Original (API)     | Nome de Campo Sugerido | Tipo    | Descrição Detalhada               |
| ------------------------ | ---------------------- | ------- | ----------------------------------- |
| `guestCheckLineItemId` | `line_item_id`       | BIGINT  | **Chave Estrangeira**.        |
| `discount_type`        | `discount_type`      | VARCHAR | Descrição do tipo de desconto.    |
| `discount_value`       | `discount_value`     | DECIMAL | Valor do desconto.                  |
| `is_percent`           | `is_percent`         | BOOLEAN | `True` se o valor for percentual. |

#### 💼 `service_charges`

| Campo Original (API)     | Nome de Campo Sugerido | Tipo    | Descrição Detalhada                  |
| ------------------------ | ---------------------- | ------- | -------------------------------------- |
| `guestCheckLineItemId` | `line_item_id`       | BIGINT  | **Chave Estrangeira**.           |
| `charge_name`          | `charge_name`        | VARCHAR | Nome da taxa (ex: "Taxa de Serviço"). |
| `charge_value`         | `charge_value`       | DECIMAL | Valor da taxa aplicada.                |

#### 💳 `tender_media`

| Campo Original (API)     | Nome de Campo Sugerido | Tipo    | Descrição Detalhada                                 |
| ------------------------ | ---------------------- | ------- | ----------------------------------------------------- |
| `guestCheckLineItemId` | `line_item_id`       | BIGINT  | **Chave Estrangeira**.                          |
| `media_type`           | `media_type`         | VARCHAR | Tipo de pagamento (ex: "Cartão de Crédito", "PIX"). |
| `amount`               | `amount`             | DECIMAL | Valor pago através desta forma de pagamento.         |

#### ❗ `error_codes`

| Campo Original (API)     | Nome de Campo Sugerido | Tipo    | Descrição Detalhada          |
| ------------------------ | ---------------------- | ------- | ------------------------------ |
| `guestCheckLineItemId` | `line_item_id`       | BIGINT  | **Chave Estrangeira**.   |
| `code`                 | `error_code`         | VARCHAR | Código do erro.               |
| `message`              | `error_message`      | VARCHAR | Descrição amigável do erro. |

---
