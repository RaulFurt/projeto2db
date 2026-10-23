-- =====================================================================
-- Controle de Patrimônio Corporativo — Iteração 2
-- 04_operacoes.sql : operações do dia a dia (INSERT / UPDATE / DELETE)
-- e demonstração das restrições de integridade e triggers.
--
-- ATENÇÃO: altera os dados. Para voltar ao estado inicial:
--     python init_db.py
-- Os comandos marcados com "ERRO ESPERADO" devem falhar de propósito.
-- Executar com:  psql -d patrimonio -f sql/04_operacoes.sql
-- (sem ON_ERROR_STOP o psql continua após cada erro)
-- =====================================================================

-- 1) Cadastro de um novo equipamento -------------------------------------
INSERT INTO equipamento (patrimonio, nome, marca, modelo, numero_serie, data_aquisicao,
                         valor, data_fim_garantia, id_categoria, id_setor, cnpj_fornecedor)
VALUES (100031, 'Notebook', 'Dell', 'Latitude 5550', 'DL5550-C31', '2026-10-01',
        7600.00, '2029-10-01', 1, 7, '11222333000144');

SELECT patrimonio, nome, status, tempo_uso_meses FROM vw_equipamento WHERE patrimonio = 100031;

-- 2) Acautelamento (retirada) -> trigger muda status para 'Em uso' ---------
INSERT INTO acautelamento (patrimonio, matricula, data_retirada)
VALUES (100031, 1009, CURRENT_DATE);

SELECT patrimonio, status FROM equipamento WHERE patrimonio = 100031;   -- 'Em uso'

-- 3) ERRO ESPERADO: mesmo equipamento para outra pessoa sem devolver --------
--    (trigger trg_acautelamento_valida / índice único parcial)
INSERT INTO acautelamento (patrimonio, matricula, data_retirada)
VALUES (100031, 1002, CURRENT_DATE);

-- 4) Devolução -> trigger volta status para 'Disponivel' -------------------
UPDATE acautelamento
   SET data_devolucao = CURRENT_DATE
 WHERE patrimonio = 100031 AND data_devolucao IS NULL;

SELECT patrimonio, status FROM equipamento WHERE patrimonio = 100031;   -- 'Disponivel'

-- 5) Registro de manutenção (seq calculado para a entidade fraca) ----------
INSERT INTO manutencao (patrimonio, seq, data, tipo, descricao, custo)
VALUES (100031,
        (SELECT COALESCE(MAX(seq), 0) + 1 FROM manutencao WHERE patrimonio = 100031),
        CURRENT_DATE, 'Preventiva', 'Instalação da imagem corporativa', 0);

-- 6) ERROS ESPERADOS de domínio / integridade ------------------------------
INSERT INTO manutencao (patrimonio, seq, data, tipo, descricao, custo)
VALUES (100031, 2, CURRENT_DATE, 'Urgente', 'Tipo inválido', 10);          -- CHECK tipo

UPDATE equipamento SET status = 'Perdido' WHERE patrimonio = 100031;       -- CHECK status

INSERT INTO equipamento (patrimonio, nome, marca, numero_serie, data_aquisicao, valor,
                         id_categoria, id_setor, cnpj_fornecedor)
VALUES (100032, 'Notebook', 'Dell', 'DL5550-C31', '2026-10-01', 7600, 1, 7,
        '11222333000144');                                                  -- UNIQUE numero_serie

INSERT INTO equipamento (patrimonio, nome, marca, numero_serie, data_aquisicao, valor,
                         id_categoria, id_setor, cnpj_fornecedor)
VALUES (100033, 'Notebook', 'Dell', 'XX-0033', '2026-10-01', 7600, 99, 7,
        '11222333000144');                                                  -- FK categoria inexistente

-- 7) Transferência de setor (equipamento muda de sala) ---------------------
UPDATE equipamento SET id_setor = 1 WHERE patrimonio = 100031;

-- 8) Exclusão do equipamento: manutenções e acautelamentos vão junto -------
--    (ON DELETE CASCADE: a entidade fraca não existe sem o dono)
SELECT COUNT(*) AS manut_antes FROM manutencao WHERE patrimonio = 100031;
DELETE FROM equipamento WHERE patrimonio = 100031;
SELECT COUNT(*) AS manut_depois FROM manutencao WHERE patrimonio = 100031;
