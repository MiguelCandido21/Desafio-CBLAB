# 🧠 ERP JSON - Modelagem Relacional para Restaurante

Este projeto tem como objetivo analisar, documentar e transformar a resposta de um endpoint de ERP (arquivo `ERP.json`) em um modelo relacional em SQL. O cenário refere-se a rede de restaurante, onde cada resposta representa uma **comanda** contendo informações de cliente, itens, taxas e detalhes operacionais.

---

## 📄 Sobre o Arquivo ERP.json

A estrutura do arquivo representa os dados de uma comanda de restaurante. Ele contém:

- Metadados do sistema (UTC, loja)
- Uma ou mais **comandas** com:
  - Informações de abertura, fechamento, mesa e funcionário
  - Impostos aplicados
  - Itens consumidos, incluindo detalhes dos produtos

---

## 🗃️ Entidades e Relacionamentos

---

### 🏢 `erp_metadata`

| Campo       | Tipo      | Descrição                                 |
| ----------- | --------- | ------------------------------------------- |
| `cur_utc` | TIMESTAMP | Data e hora da geração da resposta da API |
| `loc_ref` | VARCHAR   | Identificação da loja (ex: "99 CB CB")    |

---

### 🧾 `guest_checks` (Comandas)

| Campo                | Tipo      | Descrição                                  |
| -------------------- | --------- | -------------------------------------------- |
| `guest_check_id`   | BIGINT    | ID único da comanda                         |
| `chk_num`          | INT       | Número visível da comanda                  |
| `opn_bus_dt`       | DATE      | Data de abertura comercial                   |
| `opn_utc`          | TIMESTAMP | Data/hora UTC de abertura                    |
| `opn_lcl`          | TIMESTAMP | Data/hora local de abertura                  |
| `clsd_bus_dt`      | DATE      | Data de fechamento comercial                 |
| `clsd_utc`         | TIMESTAMP | Data/hora UTC de fechamento                  |
| `clsd_lcl`         | TIMESTAMP | Data/hora local de fechamento                |
| `last_trans_utc`   | TIMESTAMP | Última transação (UTC)                    |
| `last_trans_lcl`   | TIMESTAMP | Última transação (local)                  |
| `last_updated_utc` | TIMESTAMP | Última atualização (UTC)                  |
| `last_updated_lcl` | TIMESTAMP | Última atualização (local)                |
| `clsd_flag`        | BOOLEAN   | Se a comanda foi fechada                     |
| `gst_cnt`          | INT       | Número de convidados                        |
| `sub_ttl`          | DECIMAL   | Subtotal                                     |
| `non_txbl_sls_ttl` | DECIMAL   | Valor não tributável(gorgeta entre outros) |
| `chk_ttl`          | DECIMAL   | Total da comanda                             |
| `dsc_ttl`          | DECIMAL   | Total de descontos                           |
| `pay_ttl`          | DECIMAL   | Total pago                                   |
| `bal_due_ttl`      | DECIMAL   | Saldo pendente                               |
| `rvc_num`          | INT       | Centro de receita                            |
| `ot_num`           | INT       | Número da ordem de atendimento              |
| `oc_num`           | INT       | Número da ordem de cobrança                |
| `tbl_num`          | INT       | Número da mesa                              |
| `tbl_name`         | VARCHAR   | Nome da mesa                                 |
| `emp_num`          | INT       | Funcionário responsável(código do func)   |
| `num_srvc_rd`      | INT       | Número de rodadas de serviço               |
| `num_chk_prntd`    | INT       | Número de impressões da comanda            |

---

### 💸 `guest_check_taxes` (Impostos)

| Campo              | Tipo    | Descrição                  |
| ------------------ | ------- | ---------------------------- |
| `id`             | SERIAL  | ID do imposto (PK)           |
| `guest_check_id` | BIGINT  | FK para `guest_checks`     |
| `tax_num`        | INT     | Código do imposto           |
| `txbl_sls_ttl`   | DECIMAL | Total de vendas tributáveis |
| `tax_coll_ttl`   | DECIMAL | Valor recolhido              |
| `tax_rate`       | DECIMAL | Alíquota (%)                |
| `type`           | INT     | Tipo do imposto              |

---

### 🧾 `guest_check_detail_lines` (Itens da comanda)

| Campo                        | Tipo      | Descrição                      |
| ---------------------------- | --------- | -------------------------------- |
| `guest_check_line_item_id` | BIGINT    | ID do item (PK)                  |
| `guest_check_id`           | BIGINT    | FK para `guest_checks`         |
| `rvc_num`                  | INT       | Revenue Center                   |
| `dtl_ot_num`               | INT       | Ordem de atendimento             |
| `dtl_oc_num`               | INT       | Ordem de cobrança               |
| `line_num`                 | INT       | Linha do item                    |
| `dtl_id`                   | INT       | ID técnico                      |
| `detail_utc`               | TIMESTAMP | Hora UTC                         |
| `detail_lcl`               | TIMESTAMP | Hora local                       |
| `last_update_utc`          | TIMESTAMP | Última atualização UTC        |
| `last_update_lcl`          | TIMESTAMP | Última atualização local      |
| `bus_dt`                   | DATE      | Data comercial                   |
| `ws_num`                   | INT       | Estação de trabalho            |
| `dsp_ttl`                  | DECIMAL   | Valor unitário                  |
| `dsp_qty`                  | INT       | Quantidade exibida               |
| `agg_ttl`                  | DECIMAL   | Valor total                      |
| `agg_qty`                  | INT       | Quantidade total                 |
| `chk_emp_id`               | BIGINT    | ID do funcionário que registrou |
| `chk_emp_num`              | INT       | Número do funcionário          |
| `svc_rnd_num`              | INT       | Rodada de serviço               |
| `seat_num`                 | INT       | Número do assento               |

---

### 🍔 `menu_items` (Produtos)

| Campo                        | Tipo    | Descrição                          |
| ---------------------------- | ------- | ------------------------------------ |
| `guest_check_line_item_id` | BIGINT  | FK para `guest_check_detail_lines` |
| `mi_num`                   | INT     | Código do item do menu              |
| `mod_flag`                 | BOOLEAN | Item foi modificado?                 |
| `incl_tax`                 | DECIMAL | Imposto incluso                      |
| `active_taxes`             | VARCHAR | Impostos aplicados                   |
| `prc_lvl`                  | INT     | Nível de preço                     |

---

## 🔗 Relacionamento entre Entidades

---

## ✅ Conclusão

A modelagem acima foi baseada no princípio de normalização e integridade referencial. Cada entidade foi separada para refletir corretamente as operações de um restaurante, permitindo escalabilidade, auditoria e análise de dados.

---

## 📂 Próximos passos

- Criar `CREATE TABLE` SQL com base nesse modelo
- Inserir dados de exemplo a partir do JSON
- Armazenar múltiplas respostas no Data Lake com controle de schema (desafio 2)

---

> Desenvolvido por: **Miguel Candido**
> Desafio de Engenharia de Dados – Coco Bambu 2025
