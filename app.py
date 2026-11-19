"""Painel de monitoramento de nascimentos no Grande ABC.

Execute com:
    streamlit run app.py

Os dados utilizados são os arquivos fornecidos na pasta Conteudo/.
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "Conteudo" / "SINASC_2026_ABC.csv"
COMPRESSED_DATA_FILE = BASE_DIR / "Conteudo" / "SINASC_2026_ABC.csv.gz"
FULL_DATA_FILE = BASE_DIR / "Conteudo" / "SINASC_2026.csv"
IBGE_FILE = BASE_DIR / "Conteudo" / "IBGE_municipios.csv"

# Nome exibido junto aos três últimos gráficos.
NOME_ULTIMOS_GRAFICOS = "Miguel"

ABC_CODIGOS = {
    "351380": "Diadema",
    "352940": "Mauá",
    "354330": "Ribeirão Pires",
    "354410": "Rio Grande da Serra",
    "354780": "Santo André",
    "354870": "São Bernardo do Campo",
    "354880": "São Caetano do Sul",
}

COLUNAS_USADAS = [
    "CODMUNRES",
    "DTNASC",
    "PARTO",
    "GESTACAO",
    "GRAVIDEZ",
    "SEXO",
    "RACACOR",
    "PESO",
    "SEMAGESTAC",
    "CONSPRENAT",
    "IDADEMAE",
    "ESCMAE2010",
]

PARTO_LABELS = {
    "1": "Vaginal",
    "2": "Cesáreo",
    "9": "Ignorado",
    "": "Não informado",
}
PARTO_ORDER = ["Vaginal", "Cesáreo", "Ignorado", "Não informado"]

SEXO_LABELS = {"1": "Masculino", "2": "Feminino", "0": "Ignorado", "": "Não informado"}
SEXO_ORDER = ["Masculino", "Feminino", "Ignorado", "Não informado"]

RACA_LABELS = {
    "1": "Branca",
    "2": "Preta",
    "3": "Amarela",
    "4": "Parda",
    "5": "Indígena",
    "": "Não informado",
}
RACA_ORDER = ["Branca", "Preta", "Amarela", "Parda", "Indígena", "Não informado"]

GRAVIDEZ_LABELS = {
    "1": "Única",
    "2": "Dupla",
    "3": "Tripla ou mais",
    "9": "Ignorado",
    "": "Não informado",
}
GRAVIDEZ_ORDER = ["Única", "Dupla", "Tripla ou mais", "Ignorado", "Não informado"]

GESTACAO_LABELS = {
    "1": "Menos de 22 semanas",
    "2": "22 a 27 semanas",
    "3": "28 a 31 semanas",
    "4": "32 a 36 semanas",
    "5": "37 a 41 semanas",
    "6": "42 semanas ou mais",
    "9": "Ignorado",
    "": "Não informado",
}
GESTACAO_ORDER = [
    "Menos de 22 semanas",
    "22 a 27 semanas",
    "28 a 31 semanas",
    "32 a 36 semanas",
    "37 a 41 semanas",
    "42 semanas ou mais",
    "Ignorado",
    "Não informado",
]

ESCOLARIDADE_LABELS = {
    "0": "Sem escolaridade",
    "1": "Fundamental I",
    "2": "Fundamental II",
    "3": "Médio",
    "4": "Superior incompleto",
    "5": "Superior completo",
    "9": "Ignorado",
    "": "Não informado",
}
ESCOLARIDADE_ORDER = [
    "Sem escolaridade",
    "Fundamental I",
    "Fundamental II",
    "Médio",
    "Superior incompleto",
    "Superior completo",
    "Ignorado",
    "Não informado",
]


def rotular(serie: pd.Series, mapa: dict[str, str]) -> pd.Series:
    """Converte os códigos do SINASC para rótulos legíveis."""

    return serie.fillna("").astype(str).str.strip().map(mapa).fillna("Não informado")


@st.cache_data(show_spinner="Carregando e filtrando os dados do SINASC...")
def carregar_dados() -> pd.DataFrame:
    """Lê apenas as colunas usadas e mantém os registros do Grande ABC."""

    arquivo_dados = next(
        (arquivo for arquivo in (COMPRESSED_DATA_FILE, DATA_FILE, FULL_DATA_FILE) if arquivo.exists()),
        None,
    )
    if arquivo_dados is None:
        raise FileNotFoundError(f"Arquivo não encontrado: {DATA_FILE}")
    if not IBGE_FILE.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {IBGE_FILE}")

    dados = pd.read_csv(
        arquivo_dados,
        sep=";",
        encoding="latin1",
        dtype=str,
        usecols=COLUNAS_USADAS,
        keep_default_na=False,
    )
    for coluna in COLUNAS_USADAS:
        dados[coluna] = dados[coluna].astype(str).str.strip()

    ibge = pd.read_csv(
        IBGE_FILE,
        dtype=str,
        usecols=["Código Município Completo", "Nome_Município"],
    )
    ibge["CODMUNRES"] = ibge["Código Município Completo"].str.zfill(7).str[:6]
    nomes_ibge = (
        ibge[ibge["CODMUNRES"].isin(ABC_CODIGOS)]
        .drop_duplicates("CODMUNRES")
        .set_index("CODMUNRES")["Nome_Município"]
        .to_dict()
    )
    nomes_municipios = {codigo: nomes_ibge.get(codigo, nome) for codigo, nome in ABC_CODIGOS.items()}

    # O SINASC usa os seis primeiros dígitos do código IBGE de sete dígitos.
    dados["CODMUNRES"] = dados["CODMUNRES"].str.zfill(6)
    dados = dados[dados["CODMUNRES"].isin(nomes_municipios)].copy()
    dados["Município"] = dados["CODMUNRES"].map(nomes_municipios)

    dados["Data de nascimento"] = pd.to_datetime(
        dados["DTNASC"], format="%d%m%Y", errors="coerce"
    )
    for coluna in ["IDADEMAE", "PESO", "SEMAGESTAC", "CONSPRENAT"]:
        dados[coluna] = pd.to_numeric(dados[coluna], errors="coerce")

    dados["Tipo de parto"] = rotular(dados["PARTO"], PARTO_LABELS)
    dados["Sexo"] = rotular(dados["SEXO"], SEXO_LABELS)
    dados["Raça/cor"] = rotular(dados["RACACOR"], RACA_LABELS)
    dados["Tipo de gravidez"] = rotular(dados["GRAVIDEZ"], GRAVIDEZ_LABELS)
    dados["Faixa de gestação"] = rotular(dados["GESTACAO"], GESTACAO_LABELS)
    dados["Escolaridade materna"] = rotular(dados["ESCMAE2010"], ESCOLARIDADE_LABELS)
    dados["Consultas pré-natal"] = dados["CONSPRENAT"]
    return dados


def grafico_barras(
    tabela: pd.DataFrame,
    x: str,
    y: str,
    titulo: str,
    ordem: list[str] | None = None,
    percentual: bool = False,
    orientacao: str = "v",
):
    """Cria gráficos de barras com configuração visual consistente."""

    kwargs = {
        "data_frame": tabela,
        "x": x,
        "y": y,
        "title": titulo,
        "text_auto": ".1%" if percentual else True,
        "labels": {x: x, y: "Proporção" if percentual else "Nascimentos"},
    }
    if ordem:
        kwargs["category_orders"] = {x: ordem}
    if orientacao == "h":
        kwargs["x"], kwargs["y"] = y, x
        kwargs["labels"] = {y: "Nascimentos", x: x}
    figura = px.bar(**kwargs)
    if percentual:
        figura.update_yaxes(tickformat=".0%", range=[0, 1])
    figura.update_layout(hovermode="x unified")
    return figura


def tabela_contagem(dados: pd.DataFrame, coluna: str, ordem: list[str] | None = None) -> pd.DataFrame:
    """Retorna contagens incluindo categorias vazias quando fizer sentido."""

    resultado = dados[coluna].value_counts(dropna=False).rename_axis(coluna).reset_index(name="Nascimentos")
    if ordem:
        resultado[coluna] = pd.Categorical(resultado[coluna], categories=ordem, ordered=True)
        resultado = resultado.sort_values(coluna)
    return resultado


def titulo_com_nome(titulo: str, incluir_nome: bool = False) -> str:
    if incluir_nome:
        return f"{titulo} — Miguel"
    return titulo


st.set_page_config(page_title="Nascimentos no Grande ABC", page_icon="👶", layout="wide")

st.title("Painel de monitoramento de nascimentos")
st.subheader("Região Metropolitana do ABC Paulista — SINASC 2026")
st.caption(
    "Fonte: Sistema de Informação sobre Nascidos Vivos (SINASC), Ministério da Saúde. "
    "Os códigos foram interpretados conforme o codebook fornecido na atividade."
)

try:
    df = carregar_dados()
except Exception as erro:  # pragma: no cover - mensagem amigável para execução pelo Streamlit
    st.error(f"Não foi possível carregar os dados: {erro}")
    st.info("Instale as dependências com `pip install -r requirements.txt` e execute `streamlit run app.py`.")
    st.stop()

with st.sidebar:
    st.header("Filtros")
    municipios = st.multiselect(
        "Municípios de residência",
        options=list(ABC_CODIGOS.values()),
        default=list(ABC_CODIGOS.values()),
    )
    data_min = df["Data de nascimento"].min().date()
    data_max = df["Data de nascimento"].max().date()
    intervalo = st.date_input(
        "Período de nascimento",
        value=(data_min, data_max),
        min_value=data_min,
        max_value=data_max,
    )
    exibir_ignorados = st.checkbox("Exibir categorias ignoradas/não informadas", value=True)

if not municipios:
    st.warning("Selecione pelo menos um município para visualizar o painel.")
    st.stop()

if isinstance(intervalo, tuple) and len(intervalo) == 2:
    inicio, fim = intervalo
else:
    inicio = fim = intervalo

filtrado = df[
    df["Município"].isin(municipios)
    & df["Data de nascimento"].dt.date.between(inicio, fim)
].copy()

if not exibir_ignorados:
    categorias_validas = {"Ignorado", "Não informado"}
    for coluna in [
        "Tipo de parto",
        "Sexo",
        "Raça/cor",
        "Tipo de gravidez",
        "Faixa de gestação",
        "Escolaridade materna",
    ]:
        filtrado = filtrado[~filtrado[coluna].isin(categorias_validas)]

st.sidebar.caption(f"Registros selecionados: {len(filtrado):,}".replace(",", "."))

if filtrado.empty:
    st.warning("Nenhum registro atende aos filtros selecionados.")
    st.stop()

metricas = st.columns(4)
metricas[0].metric("Nascimentos", f"{len(filtrado):,}".replace(",", "."))
metricas[1].metric("Municípios", filtrado["Município"].nunique())
peso_valido = filtrado["PESO"].between(300, 7000)
metricas[2].metric("Peso médio", f"{filtrado.loc[peso_valido, 'PESO'].mean():.0f} g")
idade_valida = filtrado["IDADEMAE"].between(10, 60)
metricas[3].metric("Idade materna média", f"{filtrado.loc[idade_valida, 'IDADEMAE'].mean():.1f} anos")

st.divider()

# 1. Evolução mensal.
st.subheader("1. Evolução mensal dos nascimentos")
mensal = (
    filtrado.dropna(subset=["Data de nascimento"])
    .assign(Mês=lambda d: d["Data de nascimento"].dt.to_period("M").astype(str))
    .groupby("Mês", as_index=False)
    .size()
    .rename(columns={"size": "Nascimentos"})
)
fig = px.line(mensal, x="Mês", y="Nascimentos", markers=True, title="Nascimentos por mês")
fig.update_layout(hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

coluna_esquerda, coluna_direita = st.columns(2)

# 2. Tipo de parto.
with coluna_esquerda:
    st.subheader("2. Distribuição por tipo de parto")
    tabela = tabela_contagem(filtrado, "Tipo de parto", PARTO_ORDER)
    st.plotly_chart(
        grafico_barras(tabela, "Tipo de parto", "Nascimentos", "Partos por tipo", PARTO_ORDER),
        use_container_width=True,
    )

# 3. Duração da gestação por categoria.
with coluna_direita:
    st.subheader("3. Distribuição por duração da gestação")
    tabela = tabela_contagem(filtrado, "Faixa de gestação", GESTACAO_ORDER)
    st.plotly_chart(
        grafico_barras(tabela, "Faixa de gestação", "Nascimentos", "Faixas de gestação", GESTACAO_ORDER),
        use_container_width=True,
    )

coluna_esquerda, coluna_direita = st.columns(2)

# 4. Distribuição do peso.
with coluna_esquerda:
    st.subheader("4. Distribuição do peso ao nascer")
    pesos = filtrado.loc[filtrado["PESO"].between(300, 7000), ["PESO"]]
    fig = px.histogram(
        pesos,
        x="PESO",
        nbins=35,
        title="Peso ao nascer (300 g a 7.000 g)",
        labels={"PESO": "Peso (g)", "count": "Nascimentos"},
    )
    st.plotly_chart(fig, use_container_width=True)

# 5. Peso por sexo.
with coluna_direita:
    st.subheader("5. Peso ao nascer por sexo")
    pesos_sexo = filtrado.loc[
        filtrado["PESO"].between(300, 7000) & filtrado["Sexo"].isin(SEXO_ORDER),
        ["Sexo", "PESO"],
    ]
    fig = px.box(
        pesos_sexo,
        x="Sexo",
        y="PESO",
        points=False,
        category_orders={"Sexo": SEXO_ORDER},
        title="Variação do peso segundo o sexo",
        labels={"Sexo": "Sexo", "PESO": "Peso (g)"},
    )
    st.plotly_chart(fig, use_container_width=True)

coluna_esquerda, coluna_direita = st.columns(2)

# 6. Consultas de pré-natal.
with coluna_esquerda:
    st.subheader("6. Distribuição das consultas pré-natais")
    consultas = filtrado[["Consultas pré-natal"]].dropna().copy()
    consultas["Categoria"] = consultas["Consultas pré-natal"].clip(upper=20).astype(int).astype(str)
    consultas.loc[consultas["Consultas pré-natal"] > 20, "Categoria"] = "21+"
    ordem_consultas = [str(i) for i in range(21)] + ["21+"]
    tabela = consultas["Categoria"].value_counts().rename_axis("Consultas").reset_index(name="Nascimentos")
    tabela["Consultas"] = pd.Categorical(tabela["Consultas"], categories=ordem_consultas, ordered=True)
    tabela = tabela.sort_values("Consultas")
    st.plotly_chart(
        grafico_barras(tabela, "Consultas", "Nascimentos", "Consultas de pré-natal", ordem_consultas),
        use_container_width=True,
    )

# 7. Parto por idade materna.
with coluna_direita:
    st.subheader("7. Proporção de partos por idade materna")
    idade_parto = filtrado.loc[
        filtrado["IDADEMAE"].between(10, 60) & filtrado["Tipo de parto"].isin(["Vaginal", "Cesáreo"]),
        ["IDADEMAE", "Tipo de parto"],
    ].copy()
    faixas = [0, 19, 24, 29, 34, 39, 200]
    nomes_faixas = ["Até 19", "20–24", "25–29", "30–34", "35–39", "40+"]
    idade_parto["Faixa etária"] = pd.cut(
        idade_parto["IDADEMAE"], bins=faixas, labels=nomes_faixas, right=True, include_lowest=True
    )
    proporcao = pd.crosstab(idade_parto["Faixa etária"], idade_parto["Tipo de parto"], normalize="index")
    proporcao = proporcao.reindex(index=nomes_faixas, columns=["Vaginal", "Cesáreo"], fill_value=0)
    proporcao = proporcao.reset_index().melt(id_vars="Faixa etária", var_name="Tipo de parto", value_name="Proporção")
    fig = px.bar(
        proporcao,
        x="Faixa etária",
        y="Proporção",
        color="Tipo de parto",
        barmode="stack",
        category_orders={"Faixa etária": nomes_faixas, "Tipo de parto": ["Vaginal", "Cesáreo"]},
        title="Composição dos partos por faixa etária",
        labels={"Proporção": "Proporção", "Faixa etária": "Idade da mãe"},
    )
    fig.update_yaxes(tickformat=".0%", range=[0, 1])
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.caption(f"Gráficos 9, 10 e 11 — {NOME_ULTIMOS_GRAFICOS}.")

coluna_esquerda, coluna_direita = st.columns(2)

# 8. Distribuição por raça/cor.
with coluna_esquerda:
    st.subheader("8. Distribuição por raça/cor")
    tabela = tabela_contagem(filtrado, "Raça/cor", RACA_ORDER)
    st.plotly_chart(
        grafico_barras(tabela, "Raça/cor", "Nascimentos", "Raça/cor do recém-nascido", RACA_ORDER),
        use_container_width=True,
    )

# 9. Distribuição por município — responsabilidade individual.
with coluna_direita:
    st.subheader(
        titulo_com_nome("9. Distribuição por município de residência", incluir_nome=True)
    )
    tabela = tabela_contagem(filtrado, "Município", list(ABC_CODIGOS.values()))
    st.plotly_chart(
        grafico_barras(
            tabela,
            "Município",
            "Nascimentos",
            "Nascimentos por município",
            list(ABC_CODIGOS.values()),
            orientacao="h",
        ),
        use_container_width=True,
    )

coluna_esquerda, coluna_direita = st.columns(2)

# 10. Tipo de gravidez — responsabilidade individual.
with coluna_esquerda:
    st.subheader(titulo_com_nome("10. Nascimentos por tipo de gravidez", incluir_nome=True))
    tabela = tabela_contagem(filtrado, "Tipo de gravidez", GRAVIDEZ_ORDER)
    st.plotly_chart(
        grafico_barras(tabela, "Tipo de gravidez", "Nascimentos", "Tipo de gravidez", GRAVIDEZ_ORDER),
        use_container_width=True,
    )

# 11. Escolaridade e parto — responsabilidade individual.
with coluna_direita:
    st.subheader(
        titulo_com_nome("11. Escolaridade materna e tipo de parto", incluir_nome=True)
    )
    escolaridade = filtrado.loc[
        filtrado["Tipo de parto"].isin(["Vaginal", "Cesáreo"]),
        ["Escolaridade materna", "Tipo de parto"],
    ]
    cruzada = pd.crosstab(escolaridade["Escolaridade materna"], escolaridade["Tipo de parto"])
    cruzada = cruzada.reindex(index=ESCOLARIDADE_ORDER, columns=["Vaginal", "Cesáreo"], fill_value=0)
    cruzada = cruzada.reset_index().melt(
        id_vars="Escolaridade materna", var_name="Tipo de parto", value_name="Nascimentos"
    )
    fig = px.bar(
        cruzada,
        x="Escolaridade materna",
        y="Nascimentos",
        color="Tipo de parto",
        barmode="stack",
        category_orders={"Escolaridade materna": ESCOLARIDADE_ORDER},
        title="Tipos de parto por escolaridade materna",
        labels={"Escolaridade materna": "Escolaridade", "Nascimentos": "Nascimentos"},
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.markdown(
    "**Observação metodológica:** valores ignorados ou não informados são mantidos por padrão "
    "para não alterar a contagem original. Eles podem ser ocultados no filtro lateral."
)
