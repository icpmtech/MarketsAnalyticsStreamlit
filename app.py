import streamlit as st
import pandas as pd
import plotly.express as px
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente
load_dotenv()

# Conectar ao Elasticsearch
es = Elasticsearch(os.getenv("ES_URL", "http://localhost:9200"))

INDEX_NAME = "dividends"

@st.cache_data
def fetch_dividends():
    query = {
        "size": 1000,
        "query": {
            "match_all": {}
        }
    }
    res = es.search(index=INDEX_NAME, body=query)
    data = [doc["_source"] for doc in res["hits"]["hits"]]
    return pd.DataFrame(data)

def main():
    st.set_page_config(page_title="Dashboard de Dividendos", layout="wide")
    st.title("📈 Dashboard de Dividendos com Elasticsearch")

    df = fetch_dividends()

    if df.empty:
        st.warning("Nenhum dado encontrado.")
        return

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(by="date", ascending=False)

    tickers = df["ticker"].unique().tolist()
    selected_ticker = st.selectbox("Escolhe o Ticker", tickers)

    df_filtered = df[df["ticker"] == selected_ticker]

    # Filtro por data
    min_date = df_filtered["date"].min()
    max_date = df_filtered["date"].max()
    start_date, end_date = st.date_input("Período", [min_date, max_date])

    df_filtered = df_filtered[
        (df_filtered["date"] >= pd.to_datetime(start_date)) &
        (df_filtered["date"] <= pd.to_datetime(end_date))
    ]

    st.subheader(f"Dividendos - {selected_ticker}")
    fig = px.bar(df_filtered, x="date", y="amount", title="Histórico de Dividendos")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Tabela de Dividendos")
    st.dataframe(df_filtered, use_container_width=True)

if __name__ == "__main__":
    main()
