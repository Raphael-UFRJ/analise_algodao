import streamlit as st
import pandas as pd
import os
from data_cleaning import load_cotton_data, load_weather_data
from analysis import (
    analyze_seasonal_trends,
    analyze_regional_potential,
    analyze_climatic_influences,
    analyze_historical_trends,
    predict_planted_area,
)
from visualization import (
    plot_seasonal_trends,
    plot_regional_map,
    plot_climatic_influence,
    plot_historical_trends,
    plot_correlation_heatmap,
    plot_historical_trends_with_prediction,
)

# Diretório base ajustado
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
GEO_DIR = os.path.join(BASE_DIR, "data", "geo")


# Configuração inicial da página
st.set_page_config(page_title="Análise de Algodão no Brasil", layout="wide")

# Título e introdução
st.title("Análise de Dados de Plantio e Colheita de Algodão no Brasil")
st.markdown(
    """
    Este painel interativo oferece insights sobre dados históricos de algodão e condições climáticas no Brasil. 
    Descubra os melhores períodos para plantio, regiões promissoras, tendências históricas e muito mais.
    """
)

# Carregar dados
st.sidebar.header("Carregar Dados")
try:
    cotton_data_path = os.path.join(DATA_DIR, "AlgodoSerieHist.xlsx")
    weather_data_path = os.path.join(DATA_DIR, "weather_sum_all.csv")

    cotton_data = load_cotton_data(cotton_data_path)
    weather_data = load_weather_data(weather_data_path)

    st.sidebar.success("Dados carregados com sucesso!")
except Exception as e:
    st.sidebar.error(f"Erro ao carregar dados: {e}")
    st.stop()

# Sidebar para exibir dados brutos
if st.sidebar.checkbox("Exibir dados brutos de algodão"):
    st.subheader("Dados Brutos de Algodão")
    st.write(cotton_data.head(20))

if st.sidebar.checkbox("Exibir dados meteorológicos brutos"):
    st.subheader("Dados Brutos Meteorológicos")
    st.write(weather_data.head(20))

# Tabs principais
tabs = st.tabs(
    [
        "Tendências Sazonais",
        "Melhores Regiões",
        "Influência Climática",
        "Tendências Históricas",
        "Correlação de Variáveis",
        "Previsão de Area Plantada",
        "Conclusões",
    ]
)

# Aba: Tendências Sazonais
with tabs[0]:
    st.header("Tendências Sazonais")
    try:
        seasonal_trends = analyze_seasonal_trends(cotton_data, weather_data)
        st.subheader("Gráfico")
        plot_seasonal_trends(seasonal_trends)
        st.subheader("Dados de Tendências Sazonais")
        st.write(seasonal_trends)
    except Exception as e:
        st.error(f"Erro ao analisar tendências sazonais: {e}")

# Aba: Melhores Regiões
with tabs[1]:
    st.header("Melhores Regiões para Plantio")
    try:
        regional_potential = analyze_regional_potential(cotton_data, weather_data)
        st.subheader("Mapa")

        # Adicione o caminho correto para o shapefile
        shapefile_path = "./data/geo/br_states.json"
        plot_regional_map(regional_potential, shapefile_path)

        st.subheader("Detalhes por Região")
        st.write(regional_potential)
    except Exception as e:
        st.error(f"Erro ao analisar regiões: {e}")

# Aba: Influência Climática
with tabs[2]:
    st.header("Influência Climática")
    try:
        climatic_influences = analyze_climatic_influences(cotton_data, weather_data)
        st.subheader("Gráfico")
        plot_climatic_influence(climatic_influences)
        st.subheader("Detalhes da Influência Climática")
        st.write(climatic_influences)
    except Exception as e:
        st.error(f"Erro ao analisar influências climáticas: {e}")

# Aba: Tendências Históricas
with tabs[3]:
    st.header("Tendências Históricas")
    try:
        historical_trends = analyze_historical_trends(cotton_data)
        st.subheader("Gráfico de Tendências Históricas")
        plot_historical_trends(historical_trends)
        st.subheader("Dados Históricos")
        st.write(historical_trends)
    except Exception as e:
        st.error(f"Erro ao analisar tendências históricas: {e}")

# Aba: Correlação de Variáveis
with tabs[4]:
    st.header("Mapa de Correlação")
    try:
        st.subheader("Mapa de Calor")
        plot_correlation_heatmap(cotton_data, weather_data)
    except Exception as e:
        st.error(f"Erro ao gerar mapa de correlação: {e}")


# Aba: Previsão
with tabs[5]:
    st.header("Previsão da Área Plantada")

    try:
        # Entrada para selecionar o número de anos a considerar
        years_to_consider = st.number_input(
            "Anos para considerar na previsão:",
            min_value=2,
            max_value=len(cotton_data["Ano"].unique()),
            value=10,
            step=1,
        )
        # Análise de tendências históricas

        if historical_trends.empty:
            st.error("Dados históricos de área plantada não estão disponíveis.")
        else:
            # Limpar e validar dados históricos
            historical_trends["Ano"] = pd.to_numeric(
                historical_trends["Ano"], errors="coerce"
            )
            historical_trends["Area_Planted"] = pd.to_numeric(
                historical_trends["Area_Planted"], errors="coerce"
            )
            historical_trends = historical_trends.dropna(subset=["Ano", "Area_Planted"])

            # Filtrar os anos recentes
            recent_years = sorted(historical_trends["Ano"].unique())[
                -years_to_consider:
            ]
            filtered_historical_trends = historical_trends[
                historical_trends["Ano"].isin(recent_years)
            ]
            st.write("Dados Históricos Filtrados:", filtered_historical_trends)

            st.subheader("Previsão de Área Plantada")

            if len(filtered_historical_trends) < 2:
                st.warning(
                    "Dados insuficientes para previsão. É necessário pelo menos dois anos de dados históricos."
                )
            else:
                try:
                    # Previsão com dados filtrados
                    predicted_areas = predict_planted_area(
                        filtered_historical_trends, years_to_consider=years_to_consider
                    )

                    if predicted_areas.empty:
                        st.warning(
                            "Não foi possível gerar previsões para a área plantada."
                        )
                    else:
                        st.write("Previsão de Área Plantada (ha):")
                        st.write(predicted_areas)

                        # Gráfico com histórico e previsão
                        plot_historical_trends_with_prediction(
                            filtered_historical_trends, predicted_areas
                        )

                        st.success("Análise e previsão concluídas com sucesso!")
                except RuntimeError as prediction_error:
                    st.error(f"Erro ao prever área plantada: {prediction_error}")

    except Exception as e:
        st.error(f"Erro ao analisar tendências históricas com previsão: {e}")


# Aba: Conclusões
with tabs[6]:
    st.header("Conclusões e Insights")
    st.markdown(
        """
        ### **1. Melhores períodos para plantio**
        - As análises indicam que as **estações Primavera e Verão** são ideais para o plantio de algodão, devido a:
          - **Temperaturas médias elevadas** e consistentes, essenciais para o desenvolvimento das plantas.
          - **Radiação solar intensa**, que favorece o crescimento.
          - **Precipitação moderada**, evitando o excesso de umidade no solo.
        - **Recomendações**:
          - Planejar o plantio alinhado com essas estações para maximizar a produtividade.
          - Monitorar as condições climáticas durante essas épocas para ajustar práticas agrícolas.

        ### **2. Regiões com maior potencial**
        - As **regiões Nordeste e Centro-Oeste** lideram como áreas promissoras para o cultivo de algodão:
          - **Nordeste**:
            - Destaque para estados como **Bahia**, que apresenta infraestrutura e tecnologia avançadas.
            - Benefícios climáticos como alta radiação solar e precipitação controlada.
          - **Centro-Oeste**:
            - Regiões com ampla disponibilidade de terras cultiváveis e tecnologia mecanizada.
            - Expansão recente em estados como **Mato Grosso**, que apresenta forte tendência de crescimento na área plantada.
        - **Recomendações**:
          - Incentivar políticas públicas de suporte à infraestrutura agrícola nessas regiões.
          - Investir em pesquisas locais para maximizar o potencial produtivo.

        ### **3. Impactos climáticos mais significativos**
        - Variáveis climáticas com maior correlação com a área plantada:
          - **Temperatura média (0,46)**: Variável mais influente, indicando que climas estáveis e quentes são essenciais.
          - **Temperatura máxima (0,59)**: Sugere a importância de dias quentes para o crescimento ideal.
          - **Velocidade média do vento (-0,66)**: Vento excessivo é prejudicial, afetando a estabilidade das plantações.
          - **Precipitação máxima (0,35)**: Influência moderada, com o equilíbrio sendo crucial.
        - **Recomendações**:
          - Implementar sistemas de monitoramento climático em tempo real.
          - Adotar práticas agrícolas que minimizem o impacto de ventos fortes, como o uso de barreiras vegetativas.

        ### **4. Tendências históricas**
        - O crescimento histórico da área plantada reflete:
          - **Expansão da área cultivável no Brasil**: Recordes recentes em estados como Bahia e Mato Grosso.
          - **Adoção de tecnologias agrícolas modernas**, como sementes geneticamente modificadas e irrigação eficiente.
          - **Aumento no valor de mercado do algodão**, incentivando investimentos.
        - **Recomendações**:
          - Continuar investindo em tecnologias agrícolas que melhorem a eficiência e sustentabilidade.
          - Estimular o uso de práticas que protejam o solo e evitem degradação a longo prazo.

        ### **5. Previsões**
        - Com base nos modelos preditivos:
          - Estima-se uma **expansão moderada** da área plantada até 2030.
          - O crescimento dependerá de fatores como mudanças climáticas, disponibilidade de recursos e incentivos governamentais.
        - **Recomendações**:
          - Realizar planejamentos estratégicos considerando projeções climáticas.
          - Promover programas de capacitação técnica para agricultores.
        """
    )
