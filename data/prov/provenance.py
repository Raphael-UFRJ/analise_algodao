import os
from prov.model import ProvDocument, PROV
from prov.dot import prov_to_dot


def generate_provenance():
    """
    Gera um documento de proveniência para o pipeline do projeto.
    """
    prov_doc = ProvDocument()

    prov_doc.add_namespace("ufrj", "http://www.ufrj.br/")
    prov_doc.add_namespace("ppgi", "https://www.ppgi.ufrj.br")

    # Agente
    developer = prov_doc.agent(
        "ufrj:developer",
        {
            PROV["type"]: PROV["Person"],
            "prov:label": "Desenvolvedor do Projeto",
            "prov:name": "Raphael",
            "prov:email": "raphael.mauricio@gmail.com",
        },
    )

    # Entidades
    cotton_data_entity = prov_doc.entity(
        "ufrj:cotton_data",
        {
            PROV["type"]: "Dataset",
            "prov:label": "Dados do Algodão",
            "prov:location": "https://www.conab.gov.br/info-agro/safras/serie-historica-das-safras/itemlist/category/898-algodao",
        },
    )
    weather_data_entity = prov_doc.entity(
        "ufrj:weather_data",
        {
            PROV["type"]: "Dataset",
            "prov:label": "Dados Meteorológicos",
            "prov:location": "https://www.kaggle.com/datasets/gregoryoliveira/brazil-weather-information-by-inmet",
        },
    )

    # Atividades
    load_data_activity = prov_doc.activity(
        "ufrj:load_data",
        startTime="2024-11-25T10:00:00",
        endTime="2024-12-05T10:05:00",
    )
    seasonal_analysis_activity = prov_doc.activity(
        "ufrj:seasonal_analysis",
        startTime="2024-11-30T10:10:00",
        endTime="2024-12-05T10:20:00",
    )

    # Relacionamentos: Agente e Atividades
    prov_doc.wasAssociatedWith(load_data_activity, developer)
    prov_doc.wasAssociatedWith(seasonal_analysis_activity, developer)

    # Relacionamentos: Atividades e Entidades
    prov_doc.used(load_data_activity, cotton_data_entity)
    prov_doc.used(load_data_activity, weather_data_entity)
    prov_doc.used(seasonal_analysis_activity, cotton_data_entity)
    prov_doc.used(seasonal_analysis_activity, weather_data_entity)

    # Resultados gerados
    seasonal_results = prov_doc.entity(
        "ufrj:seasonal_results",
        {"prov:label": "Resultados de Tendências Sazonais"},
    )
    prov_doc.wasGeneratedBy(seasonal_results, seasonal_analysis_activity)

    return prov_doc


def save_provenance(prov_doc: ProvDocument, filename="data/outputs/provenance.json"):
    """
    Salva o documento de proveniência no formato JSON, garantindo que o diretório exista.
    """
    # Resolver o caminho absoluto com base no diretório do projeto
    base_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../..")
    )  # Vai até a raiz do projeto
    full_path = os.path.join(base_dir, filename)

    # Garantir que o diretório de saída exista
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    # Salvar o arquivo
    with open(full_path, "w") as file:
        file.write(prov_doc.serialize(indent=2))


def generate_provenance_graph(
    prov_doc, graph_filename="data/outputs/provenance_graph.png"
):
    """
    Gera e salva o gráfico de proveniência no formato PNG.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, graph_filename)

    # Garantir que o diretório de saída exista
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    try:
        # Gerar o gráfico
        dot = prov_to_dot(prov_doc)
        dot.write_png(full_path)
        return full_path
    except Exception as e:
        raise RuntimeError(f"Erro ao gerar gráfico de proveniência: {e}")


# Exemplo de uso
if __name__ == "__main__":
    prov_doc = generate_provenance()
    save_provenance(prov_doc, filename="data/outputs/provenance.json")

    # Gerar o gráfico de proveniência
    graph_path = generate_provenance_graph(prov_doc)
    print(f"Gráfico de Proveniência gerado em: {graph_path}")
