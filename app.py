"""Aplicação web de demonstração do BD de Controle de Patrimônio Corporativo.

Uso:
    pip install -r requirements.txt
    docker compose up -d     # sobe o PostgreSQL com as tabelas e os dados
    python app.py            # abre em http://127.0.0.1:5000
"""
import re
from datetime import date
from pathlib import Path

import psycopg
from flask import Flask, abort, flash, g, redirect, render_template, request, url_for
from psycopg.rows import dict_row

from init_db import DATABASE_URL, init_db

BASE_DIR = Path(__file__).resolve().parent
CONSULTAS_PATH = BASE_DIR / "sql" / "03_consultas.sql"
STATUS = ["Disponivel", "Em uso", "Em manutencao", "Descartado"]
TIPOS_MANUTENCAO = ["Preventiva", "Corretiva"]

app = Flask(__name__)
app.secret_key = "patrimonio-demo"


# ---------------------------------------------------------------------------
# Acesso ao banco
# ---------------------------------------------------------------------------
def get_db() -> psycopg.Connection:
    if "db" not in g:
        g.db = psycopg.connect(DATABASE_URL, row_factory=dict_row)
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def query(sql, params=(), one=False):
    cur = get_db().execute(sql, params)
    rows = cur.fetchall()
    return (rows[0] if rows else None) if one else rows


def execute(sql, params=()):
    """Executa um comando de escrita, faz commit e mostra o SQL na tela."""
    db = get_db()
    try:
        db.execute(sql, params)
        db.commit()
    except psycopg.Error as exc:
        db.rollback()
        flash(f"O banco recusou a operação: {exc.diag.message_primary or exc}", "error")
        flash(_inline_sql(sql, params), "sql")
        return False
    flash(_inline_sql(sql, params), "sql")
    return True


def _inline_sql(sql, params):
    """Monta o SQL com os parâmetros substituídos, só para exibição."""
    text = " ".join(sql.split())
    for p in params:
        value = "NULL" if p is None else (str(p) if isinstance(p, (int, float)) else f"'{p}'")
        text = text.replace("%s", value, 1)
    return text


# ---------------------------------------------------------------------------
# Filtros de template
# ---------------------------------------------------------------------------
@app.template_filter("brl")
def brl(value):
    if value is None:
        return "-"
    return "R$ " + f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


@app.template_filter("data")
def data_br(value):
    if not value or not re.match(r"^\d{4}-\d{2}-\d{2}$", str(value)):
        return value or "-"
    y, m, d = str(value).split("-")
    return f"{d}/{m}/{y}"


@app.template_filter("cnpj")
def cnpj_fmt(v):
    return f"{v[:2]}.{v[2:5]}.{v[5:8]}/{v[8:12]}-{v[12:]}" if v and len(v) == 14 else v


@app.template_filter("meses")
def meses(v):
    if v is None:
        return "-"
    anos, m = divmod(int(v), 12)
    partes = ([f"{anos} ano" + ("s" if anos > 1 else "")] if anos else []) + \
             ([f"{m} {'mês' if m == 1 else 'meses'}"] if m or not anos else [])
    return " e ".join(partes)


@app.context_processor
def inject_globals():
    return {"STATUS": STATUS, "hoje": date.today().isoformat()}


# ---------------------------------------------------------------------------
# Páginas
# ---------------------------------------------------------------------------
@app.route("/")
def dashboard():
    resumo = query("""
        SELECT COUNT(*)                                                   AS total,
               COUNT(*) FILTER (WHERE status = 'Em uso')                  AS em_uso,
               COUNT(*) FILTER (WHERE status = 'Disponivel')              AS disponiveis,
               COUNT(*) FILTER (WHERE status = 'Em manutencao')           AS em_manutencao,
               ROUND(SUM(valor), 2)                                       AS valor_compra,
               ROUND(SUM(valor_atual), 2)                                 AS valor_atual,
               COUNT(*) FILTER (WHERE tempo_uso_meses >= vida_util_meses) AS vencidos
          FROM vw_equipamento WHERE status <> 'Descartado'""", one=True)
    custo_manut = query("SELECT COALESCE(SUM(custo),0) AS t FROM manutencao", one=True)["t"]
    por_categoria = query("""
        SELECT categoria, COUNT(*) AS qtd, SUM(valor) AS valor
          FROM vw_equipamento WHERE status <> 'Descartado'
         GROUP BY categoria ORDER BY valor DESC""")
    substituir = query("""
        SELECT patrimonio, nome, marca, modelo, tempo_uso_meses, vida_util_meses, custo_manutencao, valor
          FROM vw_equipamento
         WHERE status <> 'Descartado' AND tempo_uso_meses >= vida_util_meses
         ORDER BY tempo_uso_meses DESC LIMIT 8""")
    garantias = query("""
        SELECT patrimonio, nome, marca, modelo, data_fim_garantia,
               data_fim_garantia - CURRENT_DATE AS dias
          FROM equipamento
         WHERE data_fim_garantia BETWEEN CURRENT_DATE AND CURRENT_DATE + 180
         ORDER BY data_fim_garantia""")
    alertas = query("""
        SELECT f.matricula, f.nome, e.patrimonio, e.nome AS equipamento, e.modelo, a.data_retirada
          FROM funcionario f
          JOIN acautelamento a ON a.matricula = f.matricula AND a.data_devolucao IS NULL
          JOIN equipamento e ON e.patrimonio = a.patrimonio
         WHERE NOT f.ativo""")
    max_valor = max((c["valor"] for c in por_categoria), default=1)
    return render_template("dashboard.html", r=resumo, custo_manut=custo_manut,
                           por_categoria=por_categoria, max_valor=max_valor,
                           substituir=substituir, garantias=garantias, alertas=alertas)


@app.route("/equipamentos")
def equipamentos():
    filtros = {k: request.args.get(k, "").strip() for k in ("q", "categoria", "bloco", "status")}
    where, params = [], []
    if filtros["q"]:
        where.append("(nome ILIKE %s OR marca ILIKE %s OR modelo ILIKE %s OR numero_serie ILIKE %s "
                     "OR CAST(patrimonio AS TEXT) LIKE %s)")
        params += [f"%{filtros['q']}%"] * 5
    for campo in ("categoria", "bloco", "status"):
        if filtros[campo]:
            where.append(f"{campo} = %s")
            params.append(filtros[campo])
    sql = "SELECT * FROM vw_equipamento" + (" WHERE " + " AND ".join(where) if where else "") + \
          " ORDER BY patrimonio"
    return render_template(
        "equipamentos.html",
        itens=query(sql, params), filtros=filtros, sql=_inline_sql(sql, params),
        categorias=[r["nome"] for r in query("SELECT nome FROM categoria ORDER BY nome")],
        blocos=[r["bloco"] for r in query("SELECT DISTINCT bloco FROM setor ORDER BY bloco")])


@app.route("/equipamentos/<int:patrimonio>")
def equipamento(patrimonio):
    e = query("SELECT * FROM vw_equipamento WHERE patrimonio = %s", (patrimonio,), one=True)
    if e is None:
        abort(404)
    historico = query("""
        SELECT a.*, f.nome, f.cargo,
               COALESCE(a.data_devolucao, CURRENT_DATE) - a.data_retirada AS dias
          FROM acautelamento a JOIN funcionario f ON f.matricula = a.matricula
         WHERE a.patrimonio = %s ORDER BY a.data_retirada DESC""", (patrimonio,))
    manutencoes = query("SELECT * FROM manutencao WHERE patrimonio = %s ORDER BY seq DESC",
                        (patrimonio,))
    funcionarios = query("SELECT matricula, nome FROM funcionario WHERE ativo ORDER BY nome")
    setores = query("SELECT * FROM setor ORDER BY bloco, sala")
    return render_template("equipamento.html", e=e, historico=historico,
                           manutencoes=manutencoes, funcionarios=funcionarios,
                           setores=setores, tipos=TIPOS_MANUTENCAO)


@app.route("/equipamentos/novo", methods=["GET", "POST"])
def equipamento_novo():
    if request.method == "POST":
        f = request.form
        ok = execute("""
            INSERT INTO equipamento (patrimonio, nome, marca, modelo, numero_serie, data_aquisicao,
                                     valor, data_fim_garantia, id_categoria, id_setor, cnpj_fornecedor)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (int(f["patrimonio"]), f["nome"], f["marca"], f["modelo"] or None, f["numero_serie"],
             f["data_aquisicao"], float(f["valor"]), f["data_fim_garantia"] or None,
             int(f["id_categoria"]), int(f["id_setor"]), f["cnpj_fornecedor"]))
        if ok:
            flash("Equipamento cadastrado.", "ok")
            return redirect(url_for("equipamento", patrimonio=int(f["patrimonio"])))
    proximo = query("SELECT COALESCE(MAX(patrimonio), 100000) + 1 AS p FROM equipamento", one=True)["p"]
    return render_template(
        "equipamento_novo.html", proximo=proximo, form=request.form,
        categorias=query("SELECT * FROM categoria ORDER BY nome"),
        setores=query("SELECT * FROM setor ORDER BY bloco, sala"),
        fornecedores=query("SELECT * FROM fornecedor ORDER BY razao_social"))


@app.post("/equipamentos/<int:patrimonio>/acautelar")
def acautelar(patrimonio):
    if execute("INSERT INTO acautelamento (patrimonio, matricula, data_retirada) VALUES (%s, %s, %s)",
               (patrimonio, int(request.form["matricula"]), request.form["data_retirada"])):
        flash("Acautelamento registrado. O trigger alterou o status para 'Em uso'.", "ok")
    return redirect(url_for("equipamento", patrimonio=patrimonio))


@app.post("/equipamentos/<int:patrimonio>/devolver")
def devolver(patrimonio):
    if execute("UPDATE acautelamento SET data_devolucao = %s "
               "WHERE patrimonio = %s AND data_devolucao IS NULL",
               (request.form["data_devolucao"], patrimonio)):
        flash("Devolução registrada. O trigger alterou o status para 'Disponivel'.", "ok")
    return redirect(url_for("equipamento", patrimonio=patrimonio))


@app.post("/equipamentos/<int:patrimonio>/manutencao")
def registrar_manutencao(patrimonio):
    f = request.form
    if execute("""
        INSERT INTO manutencao (patrimonio, seq, data, tipo, descricao, custo)
        VALUES (%s, (SELECT COALESCE(MAX(seq), 0) + 1 FROM manutencao WHERE patrimonio = %s), %s, %s, %s, %s)""",
            (patrimonio, patrimonio, f["data"], f["tipo"], f["descricao"], float(f["custo"] or 0))):
        flash("Manutenção registrada.", "ok")
    return redirect(url_for("equipamento", patrimonio=patrimonio))


@app.post("/equipamentos/<int:patrimonio>/status")
def alterar_status(patrimonio):
    if execute("UPDATE equipamento SET status = %s WHERE patrimonio = %s",
               (request.form["status"], patrimonio)):
        flash("Status atualizado.", "ok")
    return redirect(url_for("equipamento", patrimonio=patrimonio))


@app.post("/equipamentos/<int:patrimonio>/setor")
def transferir(patrimonio):
    if execute("UPDATE equipamento SET id_setor = %s WHERE patrimonio = %s",
               (int(request.form["id_setor"]), patrimonio)):
        flash("Equipamento transferido de setor.", "ok")
    return redirect(url_for("equipamento", patrimonio=patrimonio))


@app.post("/equipamentos/<int:patrimonio>/excluir")
def excluir(patrimonio):
    if execute("DELETE FROM equipamento WHERE patrimonio = %s", (patrimonio,)):
        flash(f"Equipamento {patrimonio} excluído (manutenções e acautelamentos removidos em cascata).", "ok")
        return redirect(url_for("equipamentos"))
    return redirect(url_for("equipamento", patrimonio=patrimonio))


@app.route("/funcionarios")
def funcionarios():
    itens = query("""
        SELECT f.*, s.nome AS setor, s.bloco,
               (SELECT COUNT(*) FROM acautelamento a WHERE a.matricula = f.matricula) AS total_acaut,
               (SELECT STRING_AGG(e.patrimonio || ' - ' || e.nome || ' ' || COALESCE(e.modelo, ''), '; ')
                  FROM acautelamento a JOIN equipamento e ON e.patrimonio = a.patrimonio
                 WHERE a.matricula = f.matricula AND a.data_devolucao IS NULL) AS em_posse
          FROM funcionario f JOIN setor s ON s.id_setor = f.id_setor
         ORDER BY f.nome""")
    return render_template("funcionarios.html", itens=itens)


@app.route("/fornecedores")
def fornecedores():
    itens = query("""
        SELECT f.*, COUNT(e.patrimonio) AS qtd, COALESCE(SUM(e.valor), 0) AS valor
          FROM fornecedor f LEFT JOIN equipamento e ON e.cnpj_fornecedor = f.cnpj
         GROUP BY f.cnpj ORDER BY valor DESC""")
    telefones = {}
    for t in query("SELECT * FROM fornecedor_telefone ORDER BY tipo"):
        telefones.setdefault(t["cnpj"], []).append(t)
    return render_template("fornecedores.html", itens=itens, telefones=telefones)


def carregar_consultas():
    """Lê sql/03_consultas.sql e separa os blocos marcados com -- @Q / -- @D."""
    texto = CONSULTAS_PATH.read_text(encoding="utf-8")
    consultas = []
    for bloco in texto.split("-- @Q ")[1:]:
        linhas = bloco.strip().splitlines()
        titulo = linhas[0].strip()
        descricao = linhas[1].removeprefix("-- @D").strip() if linhas[1].startswith("-- @D") else ""
        sql = "\n".join(linhas[2 if descricao else 1:]).strip()
        consultas.append({"titulo": titulo, "descricao": descricao, "sql": sql})
    return consultas


def executar_leitura(sql):
    """Executa SQL numa transação somente leitura; devolve (colunas, linhas, erro)."""
    with psycopg.connect(DATABASE_URL) as conn:
        conn.read_only = True
        try:
            conn.execute("SET LOCAL statement_timeout = '5s'")
            cur = conn.execute(sql)
            colunas = [d.name for d in cur.description] if cur.description else []
            return colunas, cur.fetchmany(500) if cur.description else [], None
        except psycopg.Error as exc:
            return [], [], exc.diag.message_primary or str(exc)
        finally:
            conn.rollback()


@app.route("/consultas")
def consultas():
    lista = carregar_consultas()
    for c in lista:
        c["colunas"], c["linhas"], c["erro"] = executar_leitura(c["sql"])
    return render_template("consultas.html", consultas=lista)


@app.route("/sql", methods=["GET", "POST"])
def console_sql():
    sql = request.form.get("sql", "SELECT * FROM vw_equipamento LIMIT 10;")
    resultado = executar_leitura(sql) if request.method == "POST" else None
    tabelas = query("SELECT table_name AS name, "
                    "CASE table_type WHEN 'VIEW' THEN 'view' ELSE 'table' END AS type "
                    "FROM information_schema.tables WHERE table_schema = 'public' "
                    "ORDER BY type, name")
    return render_template("sql.html", sql=sql, resultado=resultado, tabelas=tabelas)


@app.post("/reset")
def reset():
    init_db()
    flash("Banco recriado a partir de sql/01_schema.sql e sql/02_povoamento.sql.", "ok")
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(debug=True)
