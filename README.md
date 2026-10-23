# Controle de Patrimônio Corporativo — Projeto de BD (Iteração 2)

Banco de dados para gerenciar o inventário e o patrimônio de uma empresa de médio/grande porte:
equipamentos de TI e mobiliário, categorias contábeis, setores, fornecedores, acautelamento
(empréstimo) para funcionários e manutenções.

O repositório contém o **DER**, os **scripts SQL para criar e popular o banco**, **consultas de exemplo**
e uma **aplicação web** (Python + Flask) que usa o banco. SGBD: **PostgreSQL**.

---

## Como executar

Pré-requisitos: Docker e Python 3.10+.

```bash
docker compose up -d             # sobe o PostgreSQL 16 e já roda 01_schema.sql e 02_povoamento.sql
pip install -r requirements.txt
python app.py                    # abre a aplicação em http://127.0.0.1:5000
```

Para recriar o banco com os dados originais: `python init_db.py` ou o link "recriar banco" no rodapé da aplicação.

### Sem Docker (PostgreSQL instalado na máquina)

Crie o usuário e o banco usando o superusuário `postgres` (será pedida a senha definida na instalação):

```bash
psql -U postgres -c "CREATE USER patrimonio WITH PASSWORD 'patrimonio';"
psql -U postgres -c "CREATE DATABASE patrimonio OWNER patrimonio;"
python init_db.py      # roda sql/01_schema.sql e sql/02_povoamento.sql
python app.py
```

No Windows, se o `psql` não estiver no PATH, use o caminho completo, por exemplo
`& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -c "..."`.

Os scripts também podem ser executados direto no `psql`:

```bash
psql -U patrimonio -d patrimonio -f sql/03_consultas.sql     # consultas de exemplo
psql -U patrimonio -d patrimonio -f sql/04_operacoes.sql     # operações e testes de restrições (altera dados)
```

Para usar outro usuário, senha ou porta, defina a conexão antes de rodar a aplicação:
`DATABASE_URL=postgresql://usuario:senha@localhost:5432/patrimonio`.

Com o Docker, o `psql` também pode ser usado de dentro do container:

```bash
docker exec -it patrimonio-db psql -U patrimonio -d patrimonio
```

## Estrutura

| Caminho | Conteúdo |
|---|---|
| [docs/der_iteracao2.svg](docs/der_iteracao2.svg) | DER da iteração 2 (imagem) |
| [docs/der_iteracao2.drawio](docs/der_iteracao2.drawio) | DER da iteração 2 (editável no [diagrams.net](https://app.diagrams.net)) |
| [docs/der_iteracao1.png](docs/der_iteracao1.png) | DER da iteração 1, para comparação |
| [sql/01_schema.sql](sql/01_schema.sql) | Criação de tabelas, restrições, índices, triggers e views |
| [sql/02_povoamento.sql](sql/02_povoamento.sql) | Dados de exemplo |
| [sql/03_consultas.sql](sql/03_consultas.sql) | 13 consultas de exemplo (também executadas pela aplicação) |
| [sql/04_operacoes.sql](sql/04_operacoes.sql) | INSERT/UPDATE/DELETE do dia a dia e testes das restrições |
| [app.py](app.py), [templates/](templates/), [static/](static/) | Aplicação web |
| [docker-compose.yml](docker-compose.yml) | PostgreSQL 16 já inicializado com os scripts |
| [init_db.py](init_db.py) | Cria/recria as tabelas e os dados |
| [docs/gerar_der.py](docs/gerar_der.py) | Script que gera o `.drawio` e o `.svg` do DER |
| [docs/roteiro_apresentacao.md](docs/roteiro_apresentacao.md) | Roteiro da apresentação |

---

## 1. Minimundo

A empresa precisa de controle rigoroso sobre seus ativos físicos, principalmente equipamentos de TI
(notebooks, monitores, smartphones), impressoras e mobiliário de escritório.

- Cada equipamento adquirido é cadastrado com número de patrimônio, número de série, data e valor de
  aquisição. Ele é **classificado em uma categoria** contábil, **vinculado ao fornecedor** que o vendeu
  (para garantia e suporte) e **alocado fisicamente em um setor** da sede (bloco e sala).
- Cada categoria tem uma **vida útil**, usada para calcular a depreciação e o momento de substituição
  (ex.: notebooks a cada 4 anos).
- Fornecedores têm vários telefones (vendas, suporte).
- Funcionários são **lotados em um setor**. Com o trabalho híbrido, os equipamentos são **acautelados**
  (emprestados) aos funcionários. O sistema guarda o histórico completo: quem retirou, quando e quando
  devolveu. Um equipamento só pode estar com uma pessoa por vez.
- As equipes de TI e Facilities fazem **manutenções preventivas e corretivas**. O custo de cada uma
  é registrado para apoiar a decisão de descarte ou substituição.

## 2. Diagrama Entidade-Relacionamento (iteração 2)

![DER iteração 2](docs/der_iteracao2.svg)

Os elementos **em verde** são novos ou foram alterados em relação à primeira iteração.

**Entidades:** EQUIPAMENTO, CATEGORIA, SETOR, FORNECEDOR, FUNCIONARIO, MANUTENCAO (fraca) e ACAUTELAMENTO.

| Relacionamento | Entidades | Cardinalidade | Observação |
|---|---|---|---|
| classifica | CATEGORIA – EQUIPAMENTO | 1:N | participação total de EQUIPAMENTO |
| fornece | FORNECEDOR – EQUIPAMENTO | 1:N | participação total de EQUIPAMENTO |
| alocado em | SETOR – EQUIPAMENTO | 1:N | participação total de EQUIPAMENTO |
| recebe | EQUIPAMENTO – MANUTENCAO | 1:N | relacionamento identificador (MANUTENCAO é fraca) |
| refere-se | EQUIPAMENTO – ACAUTELAMENTO | 1:N | **novo** |
| realiza | FUNCIONARIO – ACAUTELAMENTO | 1:N | **novo** |
| lotado em | SETOR – FUNCIONARIO | 1:N | **novo** |

Atributos especiais: `localizacao` (composto: `bloco`, `sala`), `telefone` (multivalorado e composto:
`numero`, `tipo`), `tempo_uso` e `valor_atual` (derivados), `seq` (chave parcial de MANUTENCAO).

## 3. Mudanças da 1ª para a 2ª iteração

| # | O que mudou | Iteração 1 | Iteração 2 | Motivo |
|---|---|---|---|---|
| 1 | **Acautelamento** | Relacionamento N:M `utiliza` com `data_retirada` e `data_devolucao` | Entidade **ACAUTELAMENTO** com chave própria `id_acautelamento`, ligada a EQUIPAMENTO (`refere-se`) e FUNCIONARIO (`realiza`) | No mapeamento, um N:M vira uma tabela com PK `(matricula, patrimonio)`, que impede o **mesmo funcionário retirar o mesmo equipamento duas vezes**, e isso é comum no dia a dia. Com a entidade, o histórico fica completo. `data_devolucao` nula indica posse atual. |
| 2 | Tipo da manutenção | Não existia, apesar de o minimundo citar manutenções *preventivas e corretivas* | Atributo `tipo` em MANUTENCAO (`Preventiva`/`Corretiva`) | Permite comparar gastos preventivos com corretivos. |
| 3 | Garantia | Minimundo citava garantia, mas não havia atributo | `data_fim_garantia` em EQUIPAMENTO | Saber se o equipamento ainda está na garantia e acionar o suporte do fornecedor. |
| 4 | Vida útil / depreciação | Minimundo falava em depreciação, mas faltavam dados para calculá-la | `vida_util_meses` em CATEGORIA e novo derivado `valor_atual` | Depreciação linear: `valor × (1 − tempo_uso / vida_útil)`. Indica os candidatos a substituição. |
| 5 | Lotação do funcionário | FUNCIONARIO sem vínculo com SETOR | Relacionamento **lotado em** (SETOR 1:N FUNCIONARIO) | Relatórios por área e responsabilidade do gestor do setor. |
| 6 | Situação do funcionário | — | Atributo `ativo` | Auditoria: achar funcionários **desligados que não devolveram** equipamentos. |
| 7 | Telefone do fornecedor | Multivalorado simples | Multivalorado **composto** (`numero`, `tipo`: Vendas/Suporte/Geral) | A justificativa original já falava em telefone de vendas e de suporte. Agora isso é registrado. |
| 8 | Restrições de domínio | `status` livre, `numero_serie` sem restrição | `status` ∈ {Disponivel, Em uso, Em manutencao, Descartado}; `numero_serie` único | Evita dados inconsistentes. |

Regras de negócio que passaram a ser garantidas pelo próprio banco (em [01_schema.sql](sql/01_schema.sql)):

- **Índice único parcial** `ux_acautelamento_aberto`: no máximo um acautelamento em aberto por equipamento.
- **Triggers**: impedem acautelar um equipamento que não está `Disponivel`; mudam o status para `Em uso`
  na retirada e para `Disponivel` na devolução.
- **ON DELETE CASCADE** em MANUTENCAO: a entidade fraca não existe sem o equipamento dono.
- **CHECKs**: valores e custos não negativos, devolução depois da retirada, garantia depois da aquisição, CNPJ com 14 dígitos.
- **Views** `vw_equipamento` (calcula `tempo_uso`, `valor_atual`, garantia e custo de manutenção) e `vw_posse_atual`.

## 4. Modelo relacional

```mermaid
erDiagram
    CATEGORIA ||--o{ EQUIPAMENTO : classifica
    FORNECEDOR ||--o{ EQUIPAMENTO : fornece
    SETOR ||--o{ EQUIPAMENTO : "alocado em"
    SETOR ||--o{ FUNCIONARIO : "lotado em"
    FORNECEDOR ||--o{ FORNECEDOR_TELEFONE : possui
    EQUIPAMENTO ||--o{ MANUTENCAO : recebe
    EQUIPAMENTO ||--o{ ACAUTELAMENTO : "refere-se"
    FUNCIONARIO ||--o{ ACAUTELAMENTO : realiza

    CATEGORIA {
        int id_categoria PK
        varchar nome UK
        varchar descricao
        int vida_util_meses
    }
    SETOR {
        int id_setor PK
        varchar nome
        varchar bloco
        varchar sala
    }
    FORNECEDOR {
        char cnpj PK
        varchar razao_social
        varchar email
    }
    FORNECEDOR_TELEFONE {
        char cnpj PK, FK
        varchar telefone PK
        varchar tipo
    }
    FUNCIONARIO {
        int matricula PK
        varchar nome
        varchar cargo
        int id_setor FK
        int ativo
    }
    EQUIPAMENTO {
        int patrimonio PK
        varchar nome
        varchar marca
        varchar modelo
        varchar numero_serie UK
        date data_aquisicao
        decimal valor
        varchar status
        date data_fim_garantia
        int id_categoria FK
        int id_setor FK
        char cnpj_fornecedor FK
    }
    MANUTENCAO {
        int patrimonio PK, FK
        int seq PK
        date data
        varchar tipo
        varchar descricao
        decimal custo
    }
    ACAUTELAMENTO {
        int id_acautelamento PK
        int patrimonio FK
        int matricula FK
        date data_retirada
        date data_devolucao
    }
```

Mapeamento ER → relacional:

- Relacionamentos 1:N viram **chave estrangeira no lado N** (`NOT NULL` quando a participação é total).
- O atributo composto `localizacao` vira as colunas `bloco` e `sala`.
- O atributo multivalorado `telefone` vira a tabela `fornecedor_telefone`.
- A entidade fraca MANUTENCAO tem PK composta `(patrimonio, seq)`.
- Os atributos derivados `tempo_uso` e `valor_atual` não são armazenados. São calculados na view `vw_equipamento`.

## 5. Exemplos de utilização

### Aplicação web (`python app.py`)

| Página | O que mostra |
|---|---|
| **Painel** | Indicadores (valor de compra × valor depreciado, gasto com manutenção), alerta de funcionário desligado com equipamento, garantias vencendo, candidatos a substituição |
| **Equipamentos** | Listagem com filtros por categoria, **bloco**, status e busca, com o SQL gerado exibido na tela |
| **Equipamento (detalhe)** | Dados, histórico de acautelamento, manutenções e operações: acautelar, devolver, registrar manutenção, transferir de setor, mudar status, excluir |
| **Funcionários** | Lotação, situação e o que cada um tem em posse agora |
| **Fornecedores** | Telefones (multivalorado) e total fornecido |
| **Consultas** | Executa as 13 consultas de [03_consultas.sql](sql/03_consultas.sql) e mostra o SQL e o resultado |
| **Console SQL** | Executa qualquer `SELECT` (conexão somente leitura) |

Toda operação de escrita mostra o comando SQL executado. Quando o banco recusa algo (trigger, CHECK,
UNIQUE, FK), a mensagem de erro do PostgreSQL aparece na tela. O link "recriar banco", no rodapé,
volta aos dados originais.

### Consultas ([sql/03_consultas.sql](sql/03_consultas.sql))

1. Inventário com tempo de uso (atributo derivado)
2. Todos os equipamentos do Bloco Norte (atributo composto)
3. Quem está com qual equipamento agora
4. Histórico de posse de um notebook
5. Candidatos a substituição (vida útil esgotada)
6. Equipamentos cuja manutenção passou de 30% do valor (`GROUP BY` + `HAVING`)
7. Custo de manutenção por categoria e tipo
8. Fornecedores, telefones e equipamentos fornecidos (`LEFT JOIN`, `STRING_AGG`)
9. Garantias vigentes com telefone de suporte
10. Valor patrimonial por bloco e setor
11. Auditoria: funcionários desligados com equipamento
12. Ranking de uso por funcionário (`RANK()`)
13. Equipamentos que nunca foram acautelados (`NOT EXISTS`)

### Operações e restrições ([sql/04_operacoes.sql](sql/04_operacoes.sql))

Cadastro → acautelamento (trigger muda status) → tentativa de acautelar de novo (**erro esperado**) →
devolução → manutenção com `seq` automático → violações de CHECK/UNIQUE/FK (**erros esperados**) →
exclusão em cascata.
