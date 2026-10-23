-- =====================================================================
-- Controle de Patrimônio Corporativo — Iteração 2
-- 02_povoamento.sql : dados de exemplo
-- Executar depois de 01_schema.sql
-- =====================================================================

BEGIN;

-- ---------------------------------------------------------------------
-- CATEGORIA (vida útil em meses, conforme política contábil/TI)
-- ---------------------------------------------------------------------
INSERT INTO categoria (id_categoria, nome, descricao, vida_util_meses) VALUES
 (1, 'Informática - Notebooks', 'Notebooks corporativos; troca prevista a cada 4 anos', 48),
 (2, 'Informática - Monitores', 'Monitores de mesa',                                    60),
 (3, 'Telefonia Móvel',         'Smartphones corporativos',                             36),
 (4, 'Mobiliário',              'Cadeiras, mesas, armários e gaveteiros',              120),
 (5, 'Impressão',               'Impressoras e multifuncionais',                        60);

-- ---------------------------------------------------------------------
-- SETOR (localizacao = bloco + sala)
-- ---------------------------------------------------------------------
INSERT INTO setor (id_setor, nome, bloco, sala) VALUES
 (1, 'Tecnologia da Informação', 'Bloco Norte',   '101'),
 (2, 'Financeiro',               'Bloco Norte',   '204'),
 (3, 'Recursos Humanos',         'Bloco Sul',     '110'),
 (4, 'Comercial',                'Bloco Sul',     '215'),
 (5, 'Facilities',               'Bloco Central', '001'),
 (6, 'Diretoria',                'Bloco Central', '301'),
 (7, 'Almoxarifado',             'Bloco Central', '002');

-- ---------------------------------------------------------------------
-- FORNECEDOR + telefones (atributo multivalorado)
-- ---------------------------------------------------------------------
INSERT INTO fornecedor (cnpj, razao_social, email) VALUES
 ('11222333000144', 'TechNorte Distribuidora de Informática Ltda', 'vendas@technorte.com.br'),
 ('22333444000155', 'InfoSul Comércio de Equipamentos Ltda',       'comercial@infosul.com.br'),
 ('33444555000166', 'ConectaCel Telecomunicações S.A.',            'corporativo@conectacel.com.br'),
 ('44555666000177', 'MobiliArte Móveis Corporativos Ltda',         'contato@mobiliarte.com.br'),
 ('55666777000188', 'PrintMax Soluções em Impressão Ltda',         'atendimento@printmax.com.br'),
 ('66777888000199', 'ErgoOffice Equipamentos Ergonômicos Ltda',    'vendas@ergooffice.com.br');

INSERT INTO fornecedor_telefone (cnpj, telefone, tipo) VALUES
 ('11222333000144', '(84) 3201-1000', 'Vendas'),
 ('11222333000144', '(84) 3201-1050', 'Suporte'),
 ('11222333000144', '0800 701 2020',  'Suporte'),
 ('22333444000155', '(84) 3322-4000', 'Vendas'),
 ('22333444000155', '(84) 3322-4010', 'Suporte'),
 ('33444555000166', '0800 555 1010',  'Geral'),
 ('44555666000177', '(84) 3088-7700', 'Vendas'),
 ('55666777000188', '(84) 3099-8800', 'Vendas'),
 ('55666777000188', '(84) 99812-3344','Suporte'),
 ('66777888000199', '(11) 4004-3030', 'Vendas');

-- ---------------------------------------------------------------------
-- FUNCIONARIO (lotado em um setor)
-- ---------------------------------------------------------------------
INSERT INTO funcionario (matricula, nome, cargo, id_setor, ativo) VALUES
 (1001, 'Ana Beatriz Souza',     'Analista de Sistemas',    1, TRUE),
 (1002, 'Bruno Henrique Lima',   'Analista Financeiro',     2, TRUE),
 (1003, 'Carla Mendes',          'Analista de RH',          3, TRUE),
 (1004, 'Diego Fernandes',       'Executivo de Vendas',     4, TRUE),
 (1005, 'Eduarda Rocha',         'Diretora de Operações',   6, TRUE),
 (1006, 'Felipe Araújo',         'Técnico de Suporte',      1, TRUE),
 (1007, 'Gabriela Nunes',        'Coordenadora Comercial',  4, TRUE),
 (1008, 'Henrique Castro',       'Contador',                2, TRUE),
 (1009, 'Isabela Martins',       'Analista de Facilities',  5, TRUE),
 (1010, 'João Pedro Alves',      'Estagiário de TI',        1, TRUE),
 (1011, 'Larissa Teixeira',      'Executiva de Vendas',     4, FALSE),  -- desligada
 (1012, 'Marcos Vinícius Dias',  'Diretor Financeiro',      6, TRUE);

-- ---------------------------------------------------------------------
-- EQUIPAMENTO (todos entram como 'Disponivel'; os triggers de
-- acautelamento e os UPDATEs ao final ajustam o status)
-- ---------------------------------------------------------------------
INSERT INTO equipamento (patrimonio, nome, marca, modelo, numero_serie, data_aquisicao, valor, data_fim_garantia, id_categoria, id_setor, cnpj_fornecedor) VALUES
 -- Notebooks
 (100001, 'Notebook',  'Dell',    'Latitude 5420',        'DL5420-A01',  '2021-03-15', 6800.00, '2024-03-15', 1, 1, '11222333000144'),
 (100002, 'Notebook',  'Dell',    'Latitude 5420',        'DL5420-A02',  '2021-03-15', 6800.00, '2024-03-15', 1, 2, '11222333000144'),
 (100003, 'Notebook',  'Lenovo',  'ThinkPad E14 Gen 4',   'LNE14-0003',  '2022-08-10', 5900.00, '2025-08-10', 1, 4, '22333444000155'),
 (100004, 'Notebook',  'Lenovo',  'ThinkPad E14 Gen 4',   'LNE14-0004',  '2022-08-10', 5900.00, '2025-08-10', 1, 3, '22333444000155'),
 (100005, 'Notebook',  'Dell',    'Latitude 7440',        'DL7440-B05',  '2024-02-20', 9200.00, '2027-02-20', 1, 6, '11222333000144'),
 (100006, 'Notebook',  'Dell',    'Latitude 7440',        'DL7440-B06',  '2024-02-20', 9200.00, '2027-02-20', 1, 1, '11222333000144'),
 (100007, 'Notebook',  'Lenovo',  'ThinkPad T14 Gen 5',   'LNT14-0007',  '2025-06-05', 8700.00, '2028-06-05', 1, 1, '22333444000155'),
 (100008, 'Notebook',  'Lenovo',  'ThinkPad T14 Gen 5',   'LNT14-0008',  '2025-06-05', 8700.00, '2028-06-05', 1, 4, '22333444000155'),
 (100009, 'Notebook',  'Apple',   'MacBook Air M3',       'APMBA-0009',  '2025-01-12', 10500.00,'2026-01-12', 1, 6, '22333444000155'),
 (100010, 'Notebook',  'HP',      'ProBook 440 G9',       'HP440-0010',  '2023-04-18', 5400.00, '2026-04-18', 1, 2, '11222333000144'),
 (100030, 'Notebook',  'Lenovo',  'IdeaPad 3',            'LNI3-0030',   '2021-09-09', 3900.00, '2022-09-09', 1, 7, '22333444000155'),
 -- Monitores
 (100011, 'Monitor 24"', 'Dell',    'P2422H',    'DLP24-0011', '2021-03-15', 1300.00, '2024-03-15', 2, 1, '11222333000144'),
 (100012, 'Monitor 24"', 'Dell',    'P2422H',    'DLP24-0012', '2021-03-15', 1300.00, '2024-03-15', 2, 2, '11222333000144'),
 (100013, 'Monitor 27"', 'LG',      '27UL500',   'LG27-0013',  '2023-09-01', 1900.00, '2025-09-01', 2, 4, '22333444000155'),
 (100014, 'Monitor 27"', 'LG',      '27UL500',   'LG27-0014',  '2023-09-01', 1900.00, '2025-09-01', 2, 6, '22333444000155'),
 (100015, 'Monitor 24"', 'Samsung', 'S24C310',   'SS24-0015',  '2025-03-10',  950.00, '2026-03-10', 2, 3, '22333444000155'),
 (100016, 'Monitor 24"', 'Samsung', 'S24C310',   'SS24-0016',  '2025-03-10',  950.00, '2026-03-10', 2, 7, '22333444000155'),
 -- Smartphones
 (100017, 'Smartphone', 'Samsung',  'Galaxy A54', 'SGA54-0017', '2023-05-02', 2300.00, '2024-05-02', 3, 4, '33444555000166'),
 (100018, 'Smartphone', 'Samsung',  'Galaxy A54', 'SGA54-0018', '2023-05-02', 2300.00, '2024-05-02', 3, 4, '33444555000166'),
 (100019, 'Smartphone', 'Apple',    'iPhone 15',  'IP15-0019',  '2024-03-22', 5800.00, '2025-03-22', 3, 6, '33444555000166'),
 (100020, 'Smartphone', 'Motorola', 'Edge 40',    'MTE40-0020', '2022-01-14', 2600.00, '2023-01-14', 3, 3, '33444555000166'),
 (100021, 'Smartphone', 'Samsung',  'Galaxy S24', 'SGS24-0021', '2025-08-30', 4900.00, '2026-08-30', 3, 6, '33444555000166'),
 -- Mobiliário
 (100022, 'Cadeira ergonômica',       'Flexform',   'Tok',      'FLX-TOK-0022',  '2020-07-01', 1450.00, '2025-07-01', 4, 1, '44555666000177'),
 (100023, 'Cadeira ergonômica',       'Flexform',   'Tok',      'FLX-TOK-0023',  '2020-07-01', 1450.00, '2025-07-01', 4, 2, '44555666000177'),
 (100024, 'Mesa em L 160cm',          'MobiliArte', 'ML-160',   'MBA-ML160-0024','2020-07-01', 2100.00, '2023-07-01', 4, 6, '44555666000177'),
 (100025, 'Armário de aço 2 portas',  'MobiliArte', 'AR-2P',    'MBA-AR2P-0025', '2019-02-11',  980.00, NULL,         4, 5, '44555666000177'),
 (100026, 'Gaveteiro volante',        'MobiliArte', 'GV-3',     'MBA-GV-0026',   '2022-10-05',  650.00, '2024-10-05', 4, 3, '44555666000177'),
 -- Impressão
 (100027, 'Multifuncional laser', 'Brother', 'MFC-L8900CDW', 'BRL89-0027',  '2022-05-19', 7800.00, '2024-05-19', 5, 5, '55666777000188'),
 (100028, 'Impressora laser',     'HP',      'LaserJet M404','HPM404-0028', '2023-11-07', 2900.00, '2024-11-07', 5, 2, '55666777000188'),
 (100029, 'Impressora tanque',    'Epson',   'EcoTank L3250','EPL32-0029',  '2024-07-15', 1250.00, '2025-07-15', 5, 4, '55666777000188');

-- ---------------------------------------------------------------------
-- ACAUTELAMENTO — primeiro o histórico já encerrado...
-- Note que o notebook 100001 foi retirado DUAS vezes pela matrícula 1001
-- e duas pela 1010 (só é possível com a entidade ACAUTELAMENTO da iteração 2)
-- ---------------------------------------------------------------------
INSERT INTO acautelamento (patrimonio, matricula, data_retirada, data_devolucao) VALUES
 (100001, 1001, '2021-03-20', '2023-01-31'),
 (100001, 1010, '2023-02-01', '2024-02-28'),
 (100001, 1001, '2024-03-01', '2024-03-20'),   -- empréstimo temporário
 (100002, 1002, '2021-03-20', '2023-04-19'),
 (100002, 1008, '2023-04-20', '2025-01-05'),
 (100003, 1011, '2022-08-15', '2025-05-30'),
 (100010, 1002, '2023-04-20', '2024-12-20'),
 (100017, 1004, '2023-05-05', '2025-06-01'),
 (100020, 1003, '2022-01-20', '2024-11-10'),
 (100030, 1010, '2021-09-15', '2023-01-31'),
 (100030, 1009, '2023-02-10', '2026-10-14');

-- ... depois as posses em aberto (disparam o trigger que muda status para 'Em uso')
INSERT INTO acautelamento (patrimonio, matricula, data_retirada, data_devolucao) VALUES
 (100001, 1010, '2024-04-01', NULL),
 (100003, 1004, '2025-06-02', NULL),
 (100004, 1003, '2022-08-15', NULL),
 (100005, 1005, '2024-02-25', NULL),
 (100006, 1001, '2024-03-21', NULL),
 (100007, 1006, '2025-06-10', NULL),
 (100008, 1007, '2025-06-10', NULL),
 (100009, 1012, '2025-01-15', NULL),
 (100010, 1008, '2025-01-06', NULL),
 (100017, 1007, '2025-06-02', NULL),
 (100018, 1011, '2023-05-05', NULL),   -- funcionária desligada ainda com o aparelho!
 (100019, 1005, '2024-03-25', NULL),
 (100021, 1012, '2025-09-02', NULL);

-- ---------------------------------------------------------------------
-- MANUTENCAO (entidade fraca: seq reinicia para cada equipamento)
-- ---------------------------------------------------------------------
INSERT INTO manutencao (patrimonio, seq, data, tipo, descricao, custo) VALUES
 (100001, 1, '2022-03-10', 'Preventiva', 'Limpeza interna e troca de pasta térmica',             180.00),
 (100001, 2, '2023-06-22', 'Corretiva',  'Troca de bateria',                                      650.00),
 (100001, 3, '2024-09-05', 'Corretiva',  'Substituição do teclado',                               420.00),
 (100001, 4, '2025-11-18', 'Corretiva',  'Troca do SSD por unidade de 512 GB',                    590.00),
 (100001, 5, '2026-08-04', 'Corretiva',  'Reparo na dobradiça da tela',                           380.00),
 (100002, 1, '2022-03-10', 'Preventiva', 'Limpeza interna e troca de pasta térmica',             180.00),
 (100002, 2, '2024-05-14', 'Corretiva',  'Troca de bateria',                                      650.00),
 (100003, 1, '2023-08-15', 'Preventiva', 'Limpeza interna',                                       150.00),
 (100003, 2, '2025-02-03', 'Corretiva',  'Troca da tela (fora da garantia de dano acidental)',   1350.00),
 (100004, 1, '2024-01-20', 'Corretiva',  'Troca de teclado',                                      380.00),
 (100006, 1, '2025-08-12', 'Preventiva', 'Limpeza interna',                                       150.00),
 (100010, 1, '2024-10-09', 'Preventiva', 'Atualização de BIOS e limpeza',                         120.00),
 (100011, 1, '2023-02-17', 'Corretiva',  'Substituição da fonte',                                 310.00),
 (100017, 1, '2024-07-01', 'Corretiva',  'Troca de tela trincada',                                890.00),
 (100020, 1, '2023-03-12', 'Corretiva',  'Troca de bateria',                                      420.00),
 (100020, 2, '2024-10-28', 'Corretiva',  'Placa-mãe danificada, sem reparo viável (laudo de descarte)', 250.00),
 (100022, 1, '2023-07-10', 'Corretiva',  'Troca do pistão a gás',                                 220.00),
 (100024, 1, '2024-02-02', 'Corretiva',  'Reaperto e reforço da estrutura',                        90.00),
 (100027, 1, '2023-05-19', 'Preventiva', 'Revisão anual',                                         450.00),
 (100027, 2, '2024-05-20', 'Preventiva', 'Revisão anual',                                         450.00),
 (100027, 3, '2025-02-11', 'Corretiva',  'Troca da unidade fusora',                              1900.00),
 (100027, 4, '2025-05-21', 'Preventiva', 'Revisão anual',                                         480.00),
 (100027, 5, '2026-05-19', 'Preventiva', 'Revisão anual',                                         480.00),
 (100028, 1, '2025-03-03', 'Corretiva',  'Troca do rolo de tração',                               260.00),
 (100030, 1, '2022-09-20', 'Corretiva',  'Troca de bateria',                                      390.00),
 (100030, 2, '2023-11-08', 'Corretiva',  'Troca de HD por SSD',                                   450.00),
 (100030, 3, '2026-10-15', 'Corretiva',  'Equipamento não liga, em diagnóstico',                    0.00);

-- ---------------------------------------------------------------------
-- Status finais que não vêm de acautelamento
-- ---------------------------------------------------------------------
UPDATE equipamento SET status = 'Descartado'    WHERE patrimonio = 100020;
UPDATE equipamento SET status = 'Em manutencao' WHERE patrimonio = 100030;

-- Como os IDs de categoria e setor foram informados explicitamente,
-- as sequências IDENTITY são ajustadas para o próximo valor livre
SELECT setval(pg_get_serial_sequence('categoria', 'id_categoria'), (SELECT MAX(id_categoria) FROM categoria));
SELECT setval(pg_get_serial_sequence('setor', 'id_setor'),         (SELECT MAX(id_setor) FROM setor));

COMMIT;
