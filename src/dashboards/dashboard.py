import os
import sys
import streamlit as st
import pandas as pd
import plotly.express as px


PLOTLY_CONFIG = {"responsive": True}

st.set_page_config(
    page_title="Dashboard de Salários em Dados",
    page_icon="📊",
    layout="wide",
)


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

try:
    from src.pipelines.pipeline_etl import carregar_dados_tratados
except ModuleNotFoundError as e:
    st.error(f"Erro ao importar pipeline ETL: {e}")
    st.stop()

@st.cache_data(show_spinner=True)
def load_data():
    try:
        return carregar_dados_tratados(
            base_url="https://raw.githubusercontent.com/CaioAmorim-dev/data-jobs/main/salaries.csv",
            caminho_local="src/data/salarios.csv",
        )
    except Exception:
        return pd.read_csv("src/data/salarios.csv")


df = load_data()


st.sidebar.header("Filtros")

anos = st.sidebar.multiselect(
    "Ano",
    sorted(df["ano"].unique()),
    default=sorted(df["ano"].unique()),
)

senioridades = st.sidebar.multiselect(
    "Senioridade",
    sorted(df["nivel_experiencia"].unique()),
    default=sorted(df["nivel_experiencia"].unique()),
)

contratos = st.sidebar.multiselect(
    "Tipo de contrato",
    sorted(df["tipo_emprego"].unique()),
    default=sorted(df["tipo_emprego"].unique()),
)

portes = st.sidebar.multiselect(
    "Porte da empresa",
    sorted(df["porte_empresa"].unique()),
    default=sorted(df["porte_empresa"].unique()),
)


df_sel = df[
    (df["ano"].isin(anos))
    & (df["nivel_experiencia"].isin(senioridades))
    & (df["tipo_emprego"].isin(contratos))
    & (df["porte_empresa"].isin(portes))
]


st.title("📈 Análise Salarial na Área de Dados")
st.markdown(
    "Explore dados globais de salários na área de dados. "
    "Utilize os filtros à esquerda para personalizar a análise."
)
st.divider()

if df_sel.empty:
    st.warning("Nenhum dado encontrado para os filtros selecionados.")
    st.stop()


col1, col2, col3, col4 = st.columns(4)

col1.metric("Salário médio", f"${df_sel['usd'].mean():,.0f}")
col2.metric("Salário máximo", f"${df_sel['usd'].max():,.0f}")
col3.metric("Total de registros", f"{len(df_sel):,}")
col4.metric("Cargo mais frequente", df_sel["cargo"].mode()[0])

st.divider()


col_a, col_b = st.columns(2)

with col_a:
    top_cargos = (
        df_sel.groupby("cargo")["usd"]
        .mean()
        .nlargest(10)
        .sort_values()
        .reset_index()
    )

    fig_cargos = px.bar(
        top_cargos,
        x="usd",
        y="cargo",
        orientation="h",
        title="Top 10 cargos por salário médio",
        labels={"usd": "Salário médio anual (USD)", "cargo": "Cargo"},
    )

    st.plotly_chart(fig_cargos, config=PLOTLY_CONFIG)

with col_b:
    fig_hist = px.histogram(
        df_sel,
        x="usd",
        nbins=30,
        title="Distribuição salarial",
        labels={"usd": "Salário anual (USD)"},
    )

    st.plotly_chart(fig_hist, config=PLOTLY_CONFIG)

col_c, col_d = st.columns(2)

with col_c:
    salarios_ano = df_sel.groupby("ano")["usd"].mean().reset_index()

    fig_line = px.line(
        salarios_ano,
        x="ano",
        y="usd",
        markers=True,
        title="Evolução salarial ao longo dos anos",
        labels={"usd": "Salário médio (USD)", "ano": "Ano"},
    )

    st.plotly_chart(fig_line, config=PLOTLY_CONFIG)

with col_d:
    fig_box = px.box(
        df_sel,
        x="nivel_experiencia",
        y="usd",
        color="nivel_experiencia",
        title="Salário por nível de experiência",
        labels={"usd": "Salário anual (USD)", "nivel_experiencia": "Senioridade"},
    )
    fig_box.update_layout(showlegend=False)
    st.plotly_chart(fig_box, config=PLOTLY_CONFIG)

st.divider()


df_ds = df_sel[df_sel["cargo"] == "Data Scientist"]

if not df_ds.empty:
    media_pais = df_ds.groupby("residencia")["usd"].mean().reset_index()

    fig_map = px.choropleth(
        media_pais,
        locations="residencia",
        color="usd",
        locationmode="ISO-3",
        color_continuous_scale="RdYlGn",
        title="Salário médio de Data Scientist por país",
        labels={"usd": "Salário médio (USD)", "residencia": "País"},
    )

    st.plotly_chart(fig_map, config=PLOTLY_CONFIG)
else:
    st.info("Não há dados suficientes para Data Scientist com os filtros atuais.")
