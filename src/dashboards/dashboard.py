import os
import sys
import streamlit as st
import pandas as pd
import plotly.express as px

# .\.venv\Scripts\activate
# streamlit run scr\dashboards\dashboard.py

# Ajusta caminho do projeto antes de importar módulos internos 
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
try:
    import src.pipelines.pipeline_etl as pipeline_etl
except ModuleNotFoundError as e:
    st.error(f"Erro ao importar pipeline_etl: {e}")
    st.stop()


# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="Dashboard teste",
    page_icon="📊",
    layout="wide",
)

# CARREGAMENTO DOS DADOS

try:
    df = pipeline_etl.carregar_dados_tratados(
        base_url="https://raw.githubusercontent.com/CaioAmorim-dev/data-jobs/main/salaries.csv",
        caminho_local="scr/data/salarios.csv"
)
except Exception as e:
    st.warning(f"Erro ao carregar dados online ({e}). Carregando backup local...")
    df = pd.read_csv("data/salarios.csv")



# SIDEBAR - FILTROS
anos_disponiveis = sorted(df["ano"].unique())
campo_anos = st.sidebar.multiselect("Ano", anos_disponiveis, default=anos_disponiveis)

senioridades_disponiveis = sorted(df["nivel_experiencia"].unique())
campo_senioridade = st.sidebar.multiselect("Senioridade", senioridades_disponiveis, default=senioridades_disponiveis)

contratos_disponiveis = sorted(df["tipo_emprego"].unique())
campo_contratos = st.sidebar.multiselect("Tipo de emprego", contratos_disponiveis, default=contratos_disponiveis)

tamanho_empresas_disponiveis = sorted(df["porte_empresa"].unique())
campo_tamanho_empresa = st.sidebar.multiselect("Tamanho da empresa", tamanho_empresas_disponiveis, default=tamanho_empresas_disponiveis)


# FILTRAGEM DOS DADOS
df_selecionado = df[
    (df["ano"].isin(campo_anos)) &
    (df["nivel_experiencia"].isin(campo_senioridade)) &
    (df["tipo_emprego"].isin(campo_contratos)) &
    (df["porte_empresa"].isin(campo_tamanho_empresa))
]



# LAYOUT PRINCIPAL
st.title("📈 Dashboard de Análise de Salário na Área de Dados")
st.markdown("Explore dados e conheça oportunidades da área de dados no mundo todo. "
            "Use os filtros à direita para personalizar sua análise.")


# MÉTRICAS PRINCIPAIS
if not df_selecionado.empty:
    salario_medio = df_selecionado["usd"].mean()
    salario_maximo = df_selecionado["usd"].max()
    total_registros = df_selecionado.shape[0]
    cargo_mais_frequente = df_selecionado["cargo"].mode()[0]
else:
    salario_maximo, salario_medio, total_registros, cargo_mais_frequente = 0, 0, 0, ""
    st.warning("Não há dados para os filtros selecionados!")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Salário médio", f"${salario_medio:,.0f}")
col2.metric("Salário máximo", f"${salario_maximo:,.0f}")
col3.metric("Total de registros", f"{total_registros:,}")
col4.metric("Cargo mais frequente", cargo_mais_frequente)
st.markdown("---")


# GRÁFICOS
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_selecionado.empty:
        top_cargos = (
            df_selecionado.groupby("cargo")["usd"].mean().nlargest(10).sort_values(ascending=True).reset_index()
        )
        grafico_cargos = px.bar(
            data_frame=top_cargos,
            x="usd",
            y="cargo",
            orientation="h",
            title="Top 10 cargos por salário médio",
            labels={"usd": "Média salarial anual (USD)", "cargo": "Cargo"},
        )
        grafico_cargos.update_layout(title_x=0.1, yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(grafico_cargos, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para exibir.")
    
with col_graf2:
    if not df_selecionado.empty:
        grafico_hist = px.histogram(
            df_selecionado,
            x="usd",
            nbins=30,
            title="Distribuição de salários anuais",
            labels={"usd": "Faixa salarial (USD)", "count": ""}
        )
        grafico_hist.update_layout(title_x=0.1)
        st.plotly_chart(grafico_hist, use_container_width=True)
    else: 
        st.warning("Nenhum dado para exibir no gráfico de distribuição")
        

col_graf3, col_graf4 = st.columns(2)
with col_graf3:
    if not df_selecionado.empty:
        salarios_ano = df_selecionado.groupby("ano")["usd"].mean().reset_index()
        grafico_salarios = px.line(
            salarios_ano,
            x="ano",
            y="usd",
            markers=True,
            title="Aumento dos salarios com passar dos anos",
            labels={"usd": "Faixa salarial (USD)", "ano": "ano"}
        )
        grafico_salarios.update_xaxes(range=[2020, 2025], dtick=1)
        grafico_salarios.update_layout(title_x=0.1)
        st.plotly_chart(grafico_salarios, use_container_width=True)
    else:  
        st.warning("Nenhum dado disponível para exibir.")

with col_graf4:
    if not df_selecionado.empty:
        grafico_box = px.box(
            df_selecionado,
            x="nivel_experiencia",
            y="usd",
            color="nivel_experiencia",
            title="Distribuição salarial por nível de experiência",
            labels={"usd": "Salário anual (USD)", "nivel_experiencia": "Senioridade"},
            points="outliers"
        )
        grafico_box.update_layout(title_x=0.1, showlegend=False)
        st.plotly_chart(grafico_box, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de distribuição por senioridade.")


col_graf5 = st.columns(1)[0]
with col_graf5:
    if not df_selecionado.empty:
            df_ds = df_selecionado [df_selecionado["cargo"] == "Data Scientist"]
            media_ds_pais = df_ds.groupby("residencia")["usd"].mean().reset_index()
            grafico_paises = px.choropleth(
                media_ds_pais,
                locations="residencia",
                color="usd",
                color_continuous_scale="rdylgn",
                title="Salario médio de Cientista de dados por pais",
                labels={"usd": "Salario médio (USD)", "residencia": "País"},
                locationmode= "ISO-3")
            grafico_paises.update_layout(title_x=0.1)
            st.plotly_chart(grafico_paises, use_container_with=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de países")
