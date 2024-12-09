# -*- coding: utf-8 -*-
"""
# **Análise de Algodão no Brasil 🌾**
# **MAI712** - Fundamentos em Ciência de Dados
___
#### **Professores:** Sergio Serra e Jorge Zavaleta
___
#### **Desenvolvedor** Raphael Mauricio Sanches de Jesus
___
### **OBJETIVO:**
Este projeto busca realizar uma análise detalhada de dados históricos de plantio de algodão e variáveis climáticas no Brasil, com o objetivo de responder às seguintes perguntas-chave:

1. Quais são os melhores períodos para o plantio do algodão?
2. Quais regiões apresentam maior potencial para o cultivo?
3. Como as variáveis climáticas influenciam a área plantada?

#### **Requisito:**
É necessário instalar as dependências listadas no arquivo `requirements.txt` antes de executar as análises e a aplicação Streamlit.

#### **Estrutura do Código**

O código está organizado para permitir a reutilização de componentes e a manutenção clara do pipeline de análise:

- `data_cleaning.py`: Limpeza e pré-processamento dos dados de algodão e climáticos.
- `analysis.py`: Funções para análise estatística e modelagem preditiva.
- `visualization.py`: Visualização de dados por meio de gráficos e mapas interativos.
- `app.py`: Aplicação Streamlit para a interação e visualização dos resultados.
- `requirements.txt`: Dependências do projeto.
- `Dockerfile`: Configuração para execução do projeto em um ambiente Docker.

#### **Imports e Bibliotecas**

Aqui estão as principais bibliotecas utilizadas no projeto:

* [prov](https://pypi.org/project/prov/)
* [pandas](https://pandas.pydata.org/docs/) - Manipulação e análise de dados.
* [numpy](https://numpy.org/doc/) - Operações numéricas.
* [matplotlib](https://matplotlib.org/stable/index.html) e [seaborn](https://seaborn.pydata.org/) - Criação de gráficos.
* [streamlit](https://streamlit.io/) - Interface interativa para o projeto.
* [geopandas](https://geopandas.org/en/stable/) e [folium](https://python-visualization.github.io/folium/) - Visualização geográfica.
* [scikit-learn](https://scikit-learn.org/stable/) - Modelos de aprendizado de máquina para previsões.

___
"""
import os
from prov.model import ProvDocument
from prov.dot import prov_to_dot
from unidecode import unidecode
import datetime


def sanitize_label(label):
    """
    Remove caracteres especiais de uma string para evitar problemas com o pydot.
    """
    return unidecode(label.replace("\n", " ").replace("\r", " "))


def create_agents(d1):
    """
    Cria os agentes responsáveis pelo projeto no documento PROV.
    """
    agents = {}
    agents["ufrj"] = d1.agent(
        "ufrj:UFRJ",
        {
            "prov:type": "prov:Organization",
            "foaf:name": sanitize_label("Universidade Federal do Rio de Janeiro"),
        },
    )
    agents["ppgi"] = d1.agent(
        "ufrj:PPGI",
        {
            "prov:type": "prov:Organization",
            "foaf:name": sanitize_label("Programa de Pós-Graduação em Informática"),
        },
    )
    agents["mai712"] = d1.agent(
        "ufrj:MAI712",
        {
            "prov:type": "prov:Organization",
            "foaf:name": sanitize_label(
                "Disciplina de Fundamentos de Ciência de Dados"
            ),
        },
    )
    agents["developer"] = d1.agent(
        "ufrj:Raphael",
        {
            "prov:type": "prov:Person",
            "foaf:name": sanitize_label("Raphael Mauricio Sanches de Jesus"),
            "foaf:mbox": "raphael.mauricio@gmail.com",
        },
    )
    agents["script"] = d1.agent(
        "ufrj:getProv.py",
        {"prov:type": "prov:SoftwareAgent", "foaf:name": "getProv.py"},
    )

    # Relacionando os agentes
    agents["ppgi"].actedOnBehalfOf(agents["ufrj"])
    agents["mai712"].actedOnBehalfOf(agents["ppgi"])
    agents["developer"].actedOnBehalfOf(agents["mai712"])
    agents["script"].actedOnBehalfOf(agents["developer"])

    return agents


def generate_prov_document(nome_arquivo):
    """
    Gera o documento PROV com todas as entidades, atividades e agentes envolvidos.
    """
    d1 = ProvDocument()
    d1.add_namespace("ufrj", "https://www.ufrj.br")
    d1.add_namespace("foaf", "http://xmlns.com/foaf/0.1/")

    agents = create_agents(d1)
    entities = {}
    activities = {}

    # Entidades (datasets)
    entities["cotton_data"] = d1.entity(
        "ufrj:dados-algodao",
        {
            "prov:label": sanitize_label("Dataset histórico de algodão"),
            "prov:type": "foaf:Document",
            "prov:location": "data/raw/AlgodoSerieHist.xlsx",
        },
    )
    entities["weather_data"] = d1.entity(
        "ufrj:dados-clima",
        {
            "prov:label": sanitize_label("Dataset de variáveis climáticas"),
            "prov:type": "foaf:Document",
            "prov:location": "data/raw/weather_sum_all.csv",
        },
    )

    # Atividade de processamento
    activities["process_data"] = d1.activity(
        "ufrj:processamento-dados", startTime=datetime.datetime.now()
    )
    d1.used(activities["process_data"], entities["cotton_data"])
    d1.used(activities["process_data"], entities["weather_data"])

    # Entidades de resultados processados
    results = {
        "seasonal_trends": "Tendências sazonais",
        "regional_potential": "Potencial regional",
        "climatic_influences": "Influências climáticas",
        "historical_trends": "Tendências históricas",
        "predicted_areas": "Áreas previstas",
    }

    for key, label in results.items():
        entities[key] = d1.entity(
            f"ufrj:{key}",
            {"prov:label": sanitize_label(label), "prov:type": "prov:Entity"},
        )
        d1.wasGeneratedBy(entities[key], activities["process_data"])

    # Atividade de visualização
    activities["visualization"] = d1.activity(
        "ufrj:visualizacao", startTime=datetime.datetime.now()
    )
    d1.used(activities["visualization"], entities["cotton_data"])

    # Resultado da visualização
    entities["visualization_output"] = d1.entity(
        "ufrj:visualizacao-output",
        {
            "prov:label": sanitize_label("Resultado da visualização"),
            "prov:type": "prov:Entity",
        },
    )
    d1.wasGeneratedBy(entities["visualization_output"], activities["visualization"])

    # Associações
    d1.wasAssociatedWith(activities["process_data"], agents["developer"])
    d1.wasAssociatedWith(activities["process_data"], agents["script"])
    d1.wasAssociatedWith(activities["visualization"], agents["developer"])

    # Salvar gráfico PROV
    img_dir = "assets/img"
    os.makedirs(img_dir, exist_ok=True)
    output_path = os.path.join(img_dir, f"{nome_arquivo}.jpg")
    dot = prov_to_dot(d1)
    dot.write_jpg(output_path)

    return output_path


if __name__ == "__main__":
    prov_image_path = generate_prov_document("analise_algodao")
    print(f"Arquivo PROV gerado: {prov_image_path}")
