import pandas as pd
import os
import numpy as np
import plotly.express as px
import streamlit as st
import pycountry as pc

# Carregamento de dados brutos
@st.cache_data
def carregar_dados(base_url: str, caminho_local: str):
    try:
        st.info("Baixando dados de internet")
        df = pd.read_csv(base_url)
        os.makedirs(os.path.dirname(caminho_local), exist_ok=True)
        df.to_csv(caminho_local)
        st.success("Dados carregados da internet e salvos localmente")
        
    except Exception as e:
        st.warning(f"Erro ao carregar online: {e}")
        if os.path.exists(caminho_local):
            st.info("Carregando dados do cache local...")
            df = pd.read_csv(caminho_local)
        else:
            st.error("nenhum cache encontrado.")
            df = pd.DataFrame()
    return df

# Tratamentod de dados
def tratar_dados(df: pd.DataFrame) -> pd.DataFrame:
    if not df.empty:
        
        # 1. Renomeando colunas
        df.rename(columns={
            'work_year': 'ano',
            'experience_level': 'nivel_experiencia',
            'employment_type': 'tipo_emprego',
            'job_title': 'cargo',
            'salary': 'salario',
            'salary_currency': 'moeda',
            'salary_in_usd': 'usd',
            'employee_residence': 'residencia',
            'remote_ratio': 'remoto',
            'company_location': 'localizacao_empresa',
            'company_size': 'porte_empresa'
        }, inplace=True)


        # 3. Traduzindo valores categóricos
        # Nível de experiência
        senioridade_traduzida = {
            'EN': 'Junior',
            'MI': 'Pleno',
            'SE': 'Sênior',
            'EX': 'Executivo'
        }
        if "nivel_experiencia" in df.columns:
            df["nivel_experiencia"] = df["nivel_experiencia"].map(senioridade_traduzida)
        else:
            # Se a coluna não existir, cria como valor padrão ou copia de outra coluna
            df["nivel_experiencia"] = "Desconhecido"

        # Tipo de trabalho remoto
        tipo_contrato_traduzido = {
            0: 'Presencial',
            50: 'Híbrido',
            100: 'Remoto'
        }
        df["remoto"] = df["remoto"].map(tipo_contrato_traduzido)


        # 4. Tratamento de dados
        # Preenchendo valores nulos na coluna ano_trabalho
        df["ano"] = df["ano"].fillna(df["ano"].mean()).round().astype(int)
        # Cálculo da média salarial por categoria de experiência
        df["media_categoria"] = df.groupby("nivel_experiencia")["usd"].transform("mean").round()
        # Criando coluna com situação salarial (desvio percentual)
        df["situacao_salario"] = ((df["usd"] - df["media_categoria"]) / df["media_categoria"] * 100).round(2)

        # Garante que a pasta exista
        os.makedirs("scr/data", exist_ok=True)

        # Trata coluna Residencia 
        df["residencia"] = df["residencia"].apply( lambda x: pc.countries.get(alpha_2=x).alpha_3 if pc.countries.get(alpha_2=x) else None)
    
        # Salva o CSV na pasta scr/data
        df.to_csv("scr/data/dados_tratados.csv", index=False)

        return df
    else: 
        return df
    

# Carregamnto de dados tratados
def carregar_dados_tratados(base_url: str, caminho_local: str):
    df = carregar_dados(base_url, caminho_local)
    return tratar_dados(df)
