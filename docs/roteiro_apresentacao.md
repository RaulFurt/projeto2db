# Roteiro da apresentação

Antes de começar: `python init_db.py` e `python app.py`. Deixe abertos o navegador em
http://127.0.0.1:5000 e o README no GitHub.

## 1. Minimundo (~1 min)

- Patrimônio de uma empresa de médio/grande porte: TI, impressão e mobiliário.
- Todo equipamento tem **categoria** (contábil, com vida útil), **fornecedor** (garantia/suporte) e
  **setor** (bloco + sala).
- Trabalho híbrido: equipamentos são **acautelados** a funcionários, e o histórico precisa ficar guardado.
- **Manutenções** preventivas/corretivas com custo, para decidir descarte ou substituição.

## 2. DER (~2 min) — `docs/der_iteracao2.svg`

- 7 entidades. MANUTENCAO é **fraca** (borda dupla, chave parcial `seq`, identificada por `recebe`).
- Os três 1:N do EQUIPAMENTO têm participação total (linha dupla): todo equipamento tem categoria, fornecedor e setor.
- Atributo **composto** `localizacao` (bloco, sala), **multivalorado** `telefone`, **derivados** `tempo_uso` e `valor_atual`.

## 3. Mudanças da 1ª para a 2ª iteração (~2 min) — tabela da seção 3 do README

Abra lado a lado `docs/der_iteracao1.png` e `docs/der_iteracao2.svg`. O que está em verde mudou.

1. **`utiliza` (N:M) → entidade ACAUTELAMENTO.** Este é o ponto principal. Com PK `(matricula, patrimonio)`,
   a mesma pessoa não poderia pegar o mesmo notebook duas vezes. Mostre o histórico do 100001 na aplicação:
   a Ana (1001) e o João Pedro (1010) aparecem duas vezes cada.
2. Coisas que o minimundo pedia e o DER não tinha: `tipo` da manutenção, `data_fim_garantia`, `vida_util_meses` (depreciação).
3. Novo relacionamento **lotado em** e atributo `ativo` em FUNCIONARIO (auditoria de desligados).
4. Telefone com `tipo` (vendas/suporte). Domínio fixo de `status`. `numero_serie` único.

## 4. Demonstração (~4 min)

1. **Painel**: valor de compra × depreciado, alerta da funcionária desligada (Larissa) ainda com o smartphone 100018,
   candidatos a substituição.
2. **Equipamentos** → filtrar por *Bloco Norte* (atributo composto). Mostre o SQL gerado na tela.
3. Abrir um equipamento **Disponível** (ex.: 100002):
   - **Acautelar** → o status vira *Em uso* (trigger). O SQL executado aparece.
   - **Acautelar de novo** para outra pessoa → o banco **recusa** (trigger + índice único parcial).
   - **Devolver** → o status volta para *Disponível*.
   - **Registrar manutenção** → o `seq` é calculado sozinho (entidade fraca).
4. **Consultas**: mostre a 6 (manutenção > 30% do valor), a 11 (auditoria) e a 12 (ranking com `RANK()`).
5. **Console SQL** (se perguntarem algo na hora): `SELECT * FROM vw_posse_atual;`
6. No fim, clique em "recriar banco" no rodapé para voltar aos dados originais.
