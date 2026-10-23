-- =====================================================================
-- Controle de Patrimônio Corporativo — Iteração 2
-- 03_consultas.sql : exemplos de utilização do banco
--
-- Cada consulta começa com "-- @Q" (título) e "-- @D" (descrição).
-- A aplicação web lê este arquivo e executa cada bloco na página "Consultas".
-- =====================================================================

-- @Q 1. Inventário com tempo de uso (atributo derivado)
-- @D tempo_uso não é armazenado: é calculado na view vw_equipamento a partir de data_aquisicao.
SELECT patrimonio, nome, marca, modelo, categoria, setor, status,
       data_aquisicao, tempo_uso_meses
  FROM vw_equipamento
 ORDER BY tempo_uso_meses DESC;

-- @Q 2. Todos os equipamentos do Bloco Norte (atributo composto)
-- @D Exemplo citado na justificativa: filtrar por bloco, independentemente da sala.
SELECT s.bloco, s.sala, s.nome AS setor, e.patrimonio, e.nome, e.marca, e.modelo
  FROM equipamento e
  JOIN setor s ON s.id_setor = e.id_setor
 WHERE s.bloco = 'Bloco Norte'
 ORDER BY s.sala, e.patrimonio;

-- @Q 3. Quem está com qual equipamento agora
-- @D Acautelamentos em aberto (data_devolucao IS NULL), via view vw_posse_atual.
SELECT patrimonio, equipamento, matricula, funcionario, cargo,
       data_retirada, dias_em_posse
  FROM vw_posse_atual
 ORDER BY dias_em_posse DESC;

-- @Q 4. Histórico de posse do notebook 100001
-- @D Linha do tempo completa; o mesmo funcionário aparece mais de uma vez (mudança da iteração 2).
SELECT a.id_acautelamento, f.matricula, f.nome AS funcionario,
       a.data_retirada,
       COALESCE(a.data_devolucao::TEXT, '(em posse)') AS data_devolucao,
       COALESCE(a.data_devolucao, CURRENT_DATE) - a.data_retirada AS dias
  FROM acautelamento a
  JOIN funcionario f ON f.matricula = a.matricula
 WHERE a.patrimonio = 100001
 ORDER BY a.data_retirada;

-- @Q 5. Candidatos a substituição (vida útil esgotada)
-- @D Equipamentos ativos cujo tempo de uso já alcançou a vida útil da categoria (ex.: notebooks > 48 meses).
SELECT patrimonio, nome, marca, modelo, categoria, tempo_uso_meses, vida_util_meses,
       valor, valor_atual
  FROM vw_equipamento
 WHERE status <> 'Descartado'
   AND tempo_uso_meses >= vida_util_meses
 ORDER BY tempo_uso_meses DESC;

-- @Q 6. Manutenção cara demais: candidatos a descarte
-- @D Equipamentos cujo custo acumulado de manutenção passou de 30% do valor de compra (GROUP BY + HAVING).
SELECT e.patrimonio, e.nome, e.marca, e.modelo, e.valor,
       COUNT(m.seq)                           AS qtd_manutencoes,
       SUM(m.custo)                           AS custo_total,
       ROUND(100.0 * SUM(m.custo) / e.valor, 1) AS perc_do_valor
  FROM equipamento e
  JOIN manutencao m ON m.patrimonio = e.patrimonio
 GROUP BY e.patrimonio
HAVING SUM(m.custo) > 0.30 * e.valor
 ORDER BY perc_do_valor DESC;

-- @Q 7. Custo de manutenção por categoria e tipo
-- @D Compara gastos preventivos x corretivos em cada categoria.
SELECT c.nome AS categoria,
       SUM(CASE WHEN m.tipo = 'Preventiva' THEN m.custo ELSE 0 END) AS preventiva,
       SUM(CASE WHEN m.tipo = 'Corretiva'  THEN m.custo ELSE 0 END) AS corretiva,
       SUM(m.custo) AS total,
       COUNT(*)     AS qtd
  FROM manutencao m
  JOIN equipamento e ON e.patrimonio   = m.patrimonio
  JOIN categoria  c  ON c.id_categoria = e.id_categoria
 GROUP BY c.nome
 ORDER BY total DESC;

-- @Q 8. Fornecedores, telefones e equipamentos fornecidos
-- @D Atributo multivalorado agregado com STRING_AGG; LEFT JOIN mantém fornecedor sem vendas.
SELECT f.cnpj, f.razao_social,
       (SELECT STRING_AGG(t.tipo || ': ' || t.telefone, ' | ' ORDER BY t.tipo)
          FROM fornecedor_telefone t WHERE t.cnpj = f.cnpj) AS telefones,
       COUNT(e.patrimonio)            AS qtd_equipamentos,
       COALESCE(SUM(e.valor), 0)      AS valor_total
  FROM fornecedor f
  LEFT JOIN equipamento e ON e.cnpj_fornecedor = f.cnpj
 GROUP BY f.cnpj
 ORDER BY valor_total DESC;

-- @Q 9. Garantias vigentes e telefone de suporte
-- @D Equipamentos ainda na garantia, com o contato de suporte do fornecedor para abrir chamado.
SELECT e.patrimonio, e.nome, e.marca, e.modelo, e.data_fim_garantia,
       e.data_fim_garantia - CURRENT_DATE AS dias_restantes,
       f.razao_social,
       (SELECT STRING_AGG(t.telefone, ' / ') FROM fornecedor_telefone t
         WHERE t.cnpj = f.cnpj AND t.tipo IN ('Suporte', 'Geral')) AS suporte
  FROM equipamento e
  JOIN fornecedor f ON f.cnpj = e.cnpj_fornecedor
 WHERE e.data_fim_garantia >= CURRENT_DATE
 ORDER BY e.data_fim_garantia;

-- @Q 10. Valor patrimonial por bloco e setor
-- @D Valor de compra x valor atual depreciado (depreciação linear pela vida útil da categoria).
SELECT bloco, setor,
       COUNT(*)                  AS qtd,
       ROUND(SUM(valor), 2)      AS valor_compra,
       ROUND(SUM(valor_atual),2) AS valor_atual
  FROM vw_equipamento
 WHERE status <> 'Descartado'
 GROUP BY bloco, setor
 ORDER BY bloco, valor_compra DESC;

-- @Q 11. Auditoria: funcionários desligados com equipamento
-- @D Risco de perda: quem saiu da empresa e ainda não devolveu o ativo.
SELECT f.matricula, f.nome, f.cargo, e.patrimonio, e.nome AS equipamento,
       e.marca, e.modelo, a.data_retirada
  FROM funcionario f
  JOIN acautelamento a ON a.matricula  = f.matricula AND a.data_devolucao IS NULL
  JOIN equipamento  e  ON e.patrimonio = a.patrimonio
 WHERE NOT f.ativo;

-- @Q 12. Ranking de funcionários por uso de equipamentos
-- @D Total de acautelamentos e dias com equipamentos; função de janela RANK().
SELECT RANK() OVER (ORDER BY SUM(COALESCE(a.data_devolucao, CURRENT_DATE) - a.data_retirada) DESC) AS posicao,
       f.matricula, f.nome, s.nome AS setor,
       COUNT(*) AS acautelamentos,
       SUM(COALESCE(a.data_devolucao, CURRENT_DATE) - a.data_retirada) AS dias_total
  FROM funcionario f
  JOIN setor s         ON s.id_setor  = f.id_setor
  JOIN acautelamento a ON a.matricula = f.matricula
 GROUP BY f.matricula, s.nome
 ORDER BY posicao;

-- @Q 13. Equipamentos que nunca foram acautelados
-- @D NOT EXISTS: ativos fixos no setor (mobiliário, impressoras, monitores).
SELECT e.patrimonio, e.nome, e.marca, c.nome AS categoria, s.nome AS setor
  FROM equipamento e
  JOIN categoria c ON c.id_categoria = e.id_categoria
  JOIN setor     s ON s.id_setor     = e.id_setor
 WHERE NOT EXISTS (SELECT 1 FROM acautelamento a WHERE a.patrimonio = e.patrimonio)
 ORDER BY c.nome, e.patrimonio;
