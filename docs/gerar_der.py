"""Gera o DER da iteração 2 (notação de Chen) em dois formatos:

    docs/der_iteracao2.drawio  -> editável no diagrams.net (draw.io)
    docs/der_iteracao2.svg     -> imagem exibida no README

Elementos em verde são novos ou alterados em relação à iteração 1.

Uso:
    python docs/gerar_der.py
"""
import math
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# Modelo: (id, rótulo, x_centro, y_centro, opções)
# ---------------------------------------------------------------------------
ENTIDADES = [
    ("CATEGORIA", "CATEGORIA", 200, 210, {}),
    ("FORNECEDOR", "FORNECEDOR", 600, 210, {}),
    ("SETOR", "SETOR", 1120, 210, {}),
    ("EQUIPAMENTO", "EQUIPAMENTO", 720, 560, {}),
    ("MANUTENCAO", "MANUTENCAO", 180, 560, {"fraca": True}),
    ("ACAUTELAMENTO", "ACAUTELAMENTO", 1150, 560, {"novo": True}),
    ("FUNCIONARIO", "FUNCIONARIO", 1560, 560, {}),
]

RELACIONAMENTOS = [
    ("classifica", "classifica", 410, 390, {}),
    ("fornece", "fornece", 660, 390, {}),
    ("alocado", "alocado em", 920, 390, {}),
    ("lotado", "lotado em", 1560, 390, {"novo": True}),
    ("recebe", "recebe", 440, 560, {"identificador": True}),
    ("refere", "refere-se", 935, 560, {"novo": True}),
    ("realiza", "realiza", 1360, 560, {"novo": True}),
]

# (id, rótulo, x, y, dono, opções)  tipos: chave, parcial, derivado, multi, composto
ATRIBUTOS = [
    # CATEGORIA
    ("cat_id", "id_categoria", 70, 100, "CATEGORIA", {"chave": True}),
    ("cat_nome", "nome", 170, 70, "CATEGORIA", {}),
    ("cat_desc", "descricao", 270, 70, "CATEGORIA", {}),
    ("cat_vida", "vida_util_meses", 360, 110, "CATEGORIA", {"novo": True}),
    # FORNECEDOR
    ("for_cnpj", "cnpj", 470, 110, "FORNECEDOR", {"chave": True}),
    ("for_razao", "razao_social", 560, 80, "FORNECEDOR", {}),
    ("for_email", "email", 670, 100, "FORNECEDOR", {}),
    ("for_tel", "telefone", 790, 120, "FORNECEDOR", {"multi": True}),
    ("tel_num", "numero", 750, 30, "for_tel", {"novo": True}),
    ("tel_tipo", "tipo", 860, 40, "for_tel", {"novo": True}),
    # SETOR
    ("set_id", "id_setor", 990, 110, "SETOR", {"chave": True}),
    ("set_nome", "nome", 1090, 90, "SETOR", {}),
    ("set_loc", "localizacao", 1230, 110, "SETOR", {"composto": True}),
    ("set_bloco", "bloco", 1180, 30, "set_loc", {}),
    ("set_sala", "sala", 1300, 30, "set_loc", {}),
    # MANUTENCAO
    ("man_seq", "seq", 70, 450, "MANUTENCAO", {"parcial": True}),
    ("man_data", "data", 180, 425, "MANUTENCAO", {}),
    ("man_custo", "custo", 290, 450, "MANUTENCAO", {}),
    ("man_tipo", "tipo", 100, 690, "MANUTENCAO", {"novo": True}),
    ("man_desc", "descricao", 220, 700, "MANUTENCAO", {}),
    # ACAUTELAMENTO
    ("ac_id", "id_acautelamento", 1150, 425, "ACAUTELAMENTO", {"chave": True, "novo": True}),
    ("ac_ret", "data_retirada", 1040, 470, "ACAUTELAMENTO", {}),
    ("ac_dev", "data_devolucao", 1265, 470, "ACAUTELAMENTO", {}),
    # FUNCIONARIO
    ("fu_mat", "matricula", 1470, 690, "FUNCIONARIO", {"chave": True}),
    ("fu_nome", "nome", 1570, 720, "FUNCIONARIO", {}),
    ("fu_cargo", "cargo", 1670, 680, "FUNCIONARIO", {}),
    ("fu_ativo", "ativo", 1690, 470, "FUNCIONARIO", {"novo": True}),
]

# Atributos de EQUIPAMENTO distribuídos em arco abaixo da entidade
_EQ_ATRIBUTOS = [
    ("eq_pat", "patrimonio", {"chave": True}),
    ("eq_nome", "nome", {}),
    ("eq_marca", "marca", {}),
    ("eq_modelo", "modelo", {}),
    ("eq_serie", "numero_serie", {}),
    ("eq_aquis", "data_aquisicao", {}),
    ("eq_valor", "valor", {}),
    ("eq_status", "status", {}),
    ("eq_gar", "data_fim_garantia", {"novo": True}),
    ("eq_tempo", "tempo_uso", {"derivado": True}),
    ("eq_vatual", "valor_atual", {"derivado": True, "novo": True}),
]
for _k, (_i, _l, _o) in enumerate(_EQ_ATRIBUTOS):
    _ang = math.radians(160 - _k * 140 / (len(_EQ_ATRIBUTOS) - 1))
    ATRIBUTOS.append((_i, _l, round(720 + 470 * math.cos(_ang)), round(560 + 300 * math.sin(_ang)),
                      "EQUIPAMENTO", _o))

# (origem, destino, cardinalidade no lado da entidade, participação total?, novo?)
LIGACOES = [
    ("CATEGORIA", "classifica", "1", False, False),
    ("classifica", "EQUIPAMENTO", "N", True, False),
    ("FORNECEDOR", "fornece", "1", False, False),
    ("fornece", "EQUIPAMENTO", "N", True, False),
    ("SETOR", "alocado", "1", False, False),
    ("alocado", "EQUIPAMENTO", "N", True, False),
    ("SETOR", "lotado", "1", False, True),
    ("lotado", "FUNCIONARIO", "N", True, True),
    ("MANUTENCAO", "recebe", "N", True, False),
    ("recebe", "EQUIPAMENTO", "1", False, False),
    ("EQUIPAMENTO", "refere", "1", False, True),
    ("refere", "ACAUTELAMENTO", "N", True, True),
    ("ACAUTELAMENTO", "realiza", "N", True, True),
    ("realiza", "FUNCIONARIO", "1", False, True),
]

LEGENDA = ("Iteração 2 · Verde = novo/alterado em relação à iteração 1 · Sublinhado = chave primária",
           "Sublinhado tracejado = chave parcial · Elipse dupla = multivalorado · Tracejada = derivado · "
           "Cinza = composto · Linha dupla = participação total · Borda dupla = entidade fraca/relac. identificador")

# Dimensões
EW, EH = 140, 46          # entidade
RW, RH = 120, 64          # losango
AW, AH = 110, 34          # atributo

AZUL = ("#dae8fc", "#6c8ebf")
AMARELO = ("#fff2cc", "#d6b656")
VERDE = ("#d5e8d4", "#4f9a3a")
BRANCO = ("#ffffff", "#555555")
CINZA = ("#eeeeee", "#555555")


def todos_nos():
    nos = {}
    for i, lbl, x, y, o in ENTIDADES:
        nos[i] = ("ent", lbl, x, y, o)
    for i, lbl, x, y, o in RELACIONAMENTOS:
        nos[i] = ("rel", lbl, x, y, o)
    for i, lbl, x, y, _dono, o in ATRIBUTOS:
        nos[i] = ("atr", lbl, x, y, o)
    return nos


def cores(tipo, o):
    if o.get("novo"):
        return VERDE
    if tipo == "ent":
        return AZUL
    if tipo == "rel":
        return AMARELO
    return CINZA if o.get("composto") else BRANCO


# ---------------------------------------------------------------------------
# draw.io
# ---------------------------------------------------------------------------
def gerar_drawio():
    cells = ['<mxCell id="0"/>', '<mxCell id="1" parent="0"/>']
    for nid, (tipo, lbl, x, y, o) in todos_nos().items():
        fill, stroke = cores(tipo, o)
        valor = escape(lbl)
        if tipo == "ent":
            w, h = EW, EH
            style = f"shape={'ext;double=1' if o.get('fraca') else 'rect'};rounded=0;whiteSpace=wrap;html=1;fontStyle=1;"
        elif tipo == "rel":
            w, h = RW, RH
            style = "shape=rhombus;" + ("double=1;" if o.get("identificador") else "") + "whiteSpace=wrap;html=1;perimeter=rhombusPerimeter;"
        else:
            w, h = AW, AH
            style = "ellipse;whiteSpace=wrap;html=1;"
            if o.get("multi"):
                style = "ellipse;shape=doubleEllipse;whiteSpace=wrap;html=1;"
            if o.get("derivado"):
                style += "dashed=1;"
            if o.get("chave"):
                valor = f"&lt;u&gt;{valor}&lt;/u&gt;"
            if o.get("parcial"):
                valor = f"&lt;u style=&quot;text-decoration-style:dashed&quot;&gt;{valor}&lt;/u&gt;"
            if o.get("unico"):
                valor = f"{valor} (único)"
        style += f"fillColor={fill};strokeColor={stroke};fontSize=11;"
        cells.append(
            f'<mxCell id="{nid}" value="{valor}" style="{style}" vertex="1" parent="1">'
            f'<mxGeometry x="{x - w / 2}" y="{y - h / 2}" width="{w}" height="{h}" as="geometry"/></mxCell>')

    n = 0
    for i, _lbl, _x, _y, dono, o in ATRIBUTOS:
        n += 1
        cells.append(
            f'<mxCell id="ea{n}" style="endArrow=none;html=1;strokeColor=#777777;" edge="1" parent="1" '
            f'source="{dono}" target="{i}"><mxGeometry relative="1" as="geometry"/></mxCell>')
    for k, (a, b, card, total, novo) in enumerate(LIGACOES):
        cor = VERDE[1] if novo else "#333333"
        estilo = "endArrow=none;html=1;fontColor=#c00000;fontStyle=1;fontSize=13;" + \
                 (f"shape=link;strokeColor={cor};" if total else f"strokeColor={cor};")
        cells.append(
            f'<mxCell id="er{k}" value="{card}" style="{estilo}" edge="1" parent="1" source="{a}" target="{b}">'
            f'<mxGeometry relative="1" as="geometry"/></mxCell>')
    cells.append(
        f'<mxCell id="legenda" value="{escape(" · ".join(LEGENDA))}" style="text;html=1;fontSize=11;align=left;" vertex="1" parent="1">'
        f'<mxGeometry x="40" y="900" width="1700" height="30" as="geometry"/></mxCell>')

    xml = ('<mxfile host="gerar_der.py"><diagram id="der2" name="DER - Iteração 2">'
           '<mxGraphModel dx="1800" dy="960" grid="1" gridSize="10" page="1" pageWidth="1800" pageHeight="960">'
           f'<root>{"".join(cells)}</root></mxGraphModel></diagram></mxfile>')
    (OUT / "der_iteracao2.drawio").write_text(xml, encoding="utf-8")


# ---------------------------------------------------------------------------
# SVG
# ---------------------------------------------------------------------------
def borda(tipo, x, y, tx, ty):
    """Ponto na borda da forma (centro x,y) na direção de (tx,ty)."""
    dx, dy = tx - x, ty - y
    if dx == 0 and dy == 0:
        return x, y
    if tipo == "ent":
        w, h = EW / 2, EH / 2
        t = min(w / abs(dx) if dx else 1e9, h / abs(dy) if dy else 1e9)
    elif tipo == "rel":
        w, h = RW / 2, RH / 2
        t = 1 / (abs(dx) / w + abs(dy) / h)
    else:
        w, h = AW / 2, AH / 2
        t = 1 / ((dx / w) ** 2 + (dy / h) ** 2) ** 0.5
    return x + dx * t, y + dy * t


def gerar_svg():
    nos = todos_nos()
    W, H = 1780, 940
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
           'font-family="Helvetica, Arial, sans-serif" font-size="12">',
           f'<rect width="{W}" height="{H}" fill="#ffffff"/>']

    def linha(a, b, cor="#777777", dupla=False, larg=1.2):
        ta, _, xa, ya, _ = nos[a]
        tb, _, xb, yb, _ = nos[b]
        x1, y1 = borda(ta, xa, ya, xb, yb)
        x2, y2 = borda(tb, xb, yb, xa, ya)
        if dupla:
            L = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5 or 1
            nx, ny = -(y2 - y1) / L * 2.5, (x2 - x1) / L * 2.5
            for s in (1, -1):
                out.append(f'<line x1="{x1 + s * nx:.1f}" y1="{y1 + s * ny:.1f}" x2="{x2 + s * nx:.1f}" '
                           f'y2="{y2 + s * ny:.1f}" stroke="{cor}" stroke-width="{larg}"/>')
        else:
            out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{cor}" stroke-width="{larg}"/>')
        return x1, y1, x2, y2

    for i, _l, _x, _y, dono, _o in ATRIBUTOS:
        linha(dono, i)
    for a, b, card, total, novo in LIGACOES:
        x1, y1, x2, y2 = linha(a, b, VERDE[1] if novo else "#333333", total, 1.5)
        # cardinalidade perto da entidade
        ent_inicio = nos[a][0] == "ent"
        px, py = (x1, y1) if ent_inicio else (x2, y2)
        qx, qy = (x2, y2) if ent_inicio else (x1, y1)
        lx, ly = px + (qx - px) * 0.28, py + (qy - py) * 0.28
        out.append(f'<text x="{lx + 8:.1f}" y="{ly - 6:.1f}" fill="#c00000" font-weight="bold" font-size="14">{card}</text>')

    for nid, (tipo, lbl, x, y, o) in nos.items():
        fill, stroke = cores(tipo, o)
        if tipo == "ent":
            out.append(f'<rect x="{x - EW / 2}" y="{y - EH / 2}" width="{EW}" height="{EH}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
            if o.get("fraca"):
                out.append(f'<rect x="{x - EW / 2 + 4}" y="{y - EH / 2 + 4}" width="{EW - 8}" height="{EH - 8}" fill="none" stroke="{stroke}" stroke-width="1.2"/>')
            out.append(f'<text x="{x}" y="{y + 4}" text-anchor="middle" font-weight="bold">{escape(lbl)}</text>')
        elif tipo == "rel":
            pts = f"{x},{y - RH / 2} {x + RW / 2},{y} {x},{y + RH / 2} {x - RW / 2},{y}"
            out.append(f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
            if o.get("identificador"):
                pts2 = f"{x},{y - RH / 2 + 7} {x + RW / 2 - 12},{y} {x},{y + RH / 2 - 7} {x - RW / 2 + 12},{y}"
                out.append(f'<polygon points="{pts2}" fill="none" stroke="{stroke}" stroke-width="1.2"/>')
            out.append(f'<text x="{x}" y="{y + 4}" text-anchor="middle">{escape(lbl)}</text>')
        else:
            dash = ' stroke-dasharray="4 3"' if o.get("derivado") else ""
            out.append(f'<ellipse cx="{x}" cy="{y}" rx="{AW / 2}" ry="{AH / 2}" fill="{fill}" stroke="{stroke}"{dash}/>')
            if o.get("multi"):
                out.append(f'<ellipse cx="{x}" cy="{y}" rx="{AW / 2 - 4}" ry="{AH / 2 - 4}" fill="none" stroke="{stroke}"/>')
            texto = lbl + (" (único)" if o.get("unico") else "")
            fs = 11 if len(texto) > 15 else 12
            out.append(f'<text x="{x}" y="{y + 4}" text-anchor="middle" font-size="{fs}">{escape(texto)}</text>')
            if o.get("chave") or o.get("parcial"):
                meia = len(lbl) * fs * 0.29
                d = ' stroke-dasharray="3 2"' if o.get("parcial") else ""
                out.append(f'<line x1="{x - meia:.1f}" y1="{y + 7}" x2="{x + meia:.1f}" y2="{y + 7}" stroke="#222"{d}/>')

    for k, parte in enumerate(LEGENDA):
        out.append(f'<text x="30" y="{H - 40 + k * 18}" font-size="12" fill="#444">{escape(parte)}</text>')
    out.append("</svg>")
    (OUT / "der_iteracao2.svg").write_text("\n".join(out), encoding="utf-8")


if __name__ == "__main__":
    gerar_drawio()
    gerar_svg()
    print("Gerados docs/der_iteracao2.drawio e docs/der_iteracao2.svg")
