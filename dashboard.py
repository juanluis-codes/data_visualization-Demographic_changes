# IMPORTS
import streamlit as st
import altair as alt
import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt

def createTemporalEvolutionProvincesChart(data, metric):
    provinces = ["28-Madrid", "08-Barcelona", "46-Valencia/València", "Total"]
    
    data_filtered = data[
        (data[metric].notna()) &
        (data[metric] != "") &
        (data["Sexo"] == "Total") &
        (data["Provincias"].isin(provinces))  
    ]

    if metric == "Poblacion":
        data_filtered = data_filtered[
            (data["Periodo"] != 1996)  
        ]
    
    chart = alt.Chart(data_filtered).mark_line().encode(
        x="Periodo:O",
        y=f"{metric}",
        color="Provincias",
        tooltip=["Periodo:O", f"{metric}"]
    ).properties(
        title="Evolución temporal de la población en España y sus tres provincias más pobladas",
    ).interactive()
    
    return chart

def createTemporalEvolutionChart(data):
    data_filtered = data[
        (data["Poblacion"].notna()) &
        (data["Poblacion"] != "") &
        (data["Defunciones"].notna()) &
        (data["Defunciones"] != "") &
        (data["Nacimientos"].notna()) &
        (data["Nacimientos"] != "") &
        (data["Delitos"].notna()) &
        (data["Delitos"] != "") &
        (data["Sexo"] == "Total") &
        (data["Provincias"] == "Total")
    ]

    colors = alt.Scale(domain=["Defunciones", "Nacimientos", "Delitos"],
                        range=["red", "green", "yellow"])
    
    chart = alt.Chart(data_filtered).encode(
        x=alt.X("Periodo:O", title="Periodo"),
        tooltip=["Periodo:O", "Defunciones", "Nacimientos", "Delitos"]
    ).properties(
        title="Comparación de tendencias temporales de fenómenos demográficos"
    )

    deaths = chart.mark_line().encode(
        y=alt.Y("Defunciones:Q", title="Cantidad"),
        color=alt.Color("atributo:N", scale=colors, legend=alt.Legend(title="Atributo"))
    ).transform_calculate(atributo="'Defunciones'")

    births = chart.mark_line().encode(
        y=alt.Y("Nacimientos:Q", title="Cantidad"),
        color=alt.Color("atributo:N", scale=colors, legend=None)
    ).transform_calculate(atributo="'Nacimientos'")

    crimes = chart.mark_line().encode(
        y=alt.Y("Delitos:Q", title="Cantidad"),
        color=alt.Color("atributo:N", scale=colors, legend=None)
    ).transform_calculate(atributo="'Delitos'")

    # Combinar todas las líneas en un solo gráfico
    final_chart = (deaths + births + crimes).interactive()
    
    return final_chart

def calculatePopulationGrowth(data):
    dict = {}
    
    for provincia in data["Provincias"].unique():
        data_sp = data[
            (data["Provincias"] == f"{provincia}") & 
            (data["Sexo"] == "Total") & 
            (data["Periodo"].isin([1998, 2021]))
        ]

        population_1998 = data_sp[data_sp["Periodo"] == 1998]["Poblacion"].values[0]
        population_2021 = data_sp[data_sp["Periodo"] == 2021]["Poblacion"].values[0]
        
        crecimiento = population_2021 - population_1998
        
        dict[provincia] = crecimiento
        
    return dict

def createPopulationGrowthChart(data):
    dict = calculatePopulationGrowth(data)
    
    data = pd.DataFrame(list(dict.items()), columns=["Provincia", "Cambio poblacion"])
    
    data_filtered = data[~data["Provincia"].isin(["Total"])]
    
    chart = alt.Chart(data_filtered).mark_bar().encode(
        x=alt.X("Cambio poblacion:Q", title="Cambio de población"),
        y=alt.Y("Provincia:N", sort="-x", title="Provincia"),
        tooltip=["Provincia", "Cambio poblacion"]
    ).properties(
        title="Cambio de población por provincia (1998-2021)",
        width=800,
        height=600
    ).interactive()
    
    return chart

def createCrimesCorrelationChart(data, feature1, feature2):
    data_filtered = data[
        (data[feature1] != "") &
        (data[feature1].notna()) &
        (data[feature2] != "") &
        (data[feature2].notna()) &
        (data["Sexo"] == "Total")
    ]
    
    data_filtered = data_filtered[~data_filtered["Provincias"].isin(["No residente", "Total"])]
    
   
    chart = alt.Chart(data_filtered).mark_point().encode(
        x=alt.X(feature1, type="quantitative"),
        y=alt.Y(feature2, type="quantitative"),
        color=alt.Color("Provincias")
    )
    
    return chart

def createSexAccumulatedChart(data, metric):
    data_filtered = data[
        (data["Provincias"] != "") &
        (data["Provincias"].notna()) &
        (data[f"{metric}"] != "") &
        (data[f"{metric}"].notna()) &
        (data["Provincias"] == "Total") &
        (data["Sexo"] != "Total")
    ]
    
    chart = alt.Chart(data_filtered).mark_bar().encode(
        x="Periodo:O",
        y=f"{metric}",
        color="Sexo:N",
        tooltip=["Periodo", f"{metric}", "Sexo"]
    ).properties(
        title=f"Evolución de {metric} por género a lo largo del tiempo",
        width=600,
        height=400
    )
    
    return chart

def createSexPieChart(data, metric):
    data_filtered = data[
        (data["Provincias"] != "") &
        (data["Provincias"].notna()) &
        (data["Provincias"] == "Total") &
        (data[f"{metric}"] != "") &
        (data[f"{metric}"].notna()) &
        (data["Periodo"] == 2021) &
        (data["Sexo"] != "Total")
    ]
    
    chart = alt.Chart(data_filtered).mark_arc().encode(
        theta=alt.Theta(field=f"{metric}", type="quantitative"),
        color=alt.Color(field="Sexo", type="nominal"),
        tooltip=["Sexo", f"{metric}"]
    ).properties(
        title=f"Proporción de {metric} por género (2021)"
    )
    
    return chart

# Función para crear el mapa con Matplotlib
def create_matplotlib_map(data, df_geo, metric):
    df_geo = gpd.read_file('datasets/provincias.geojson')

    # Verificar y reproyectar si es necesario
    if df_geo.crs != "EPSG:3857":
        df_geo = df_geo.to_crs("EPSG:3857")

    # Filtrar el dataframe 'out.csv' para el año 2021 y el sexo "Total"
    df_filtered = data[(data['Periodo'] == 2021) & (data['Sexo'] == 'Total') & (~data['Provincias'].isin(['Total']))]
    df_filtered['NAME_2'] = df_filtered['Provincias'].apply(lambda x: x.split('/')[0].split('-')[1].strip())


    # Mezclar los dataframes por la columna "Provincias" y "NAME_2"
    merged_df = df_geo.merge(df_filtered, on='NAME_2')

    # Crear el mapa de calor
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_xlabel("Longitud")
    ax.set_ylabel("Latitud")
    merged_df.plot(column=f'{metric}', cmap='OrRd', linewidth=0.8, ax=ax, edgecolor='0', legend=True)
    plt.title(f'Mapa de Calor de la {metric.lower()} en España (2021)')
    plt.axis('off')
    
    return fig

def load_data(path):
    if(path.split(".")[1] == "csv"):
        data = pd.read_csv(path, sep=",", converters={"Poblacion": lambda x: int(x.replace(".", "")) if isinstance(x, str) and x.replace(".", "").isdigit() else np.nan})
    else:
        data = gpd.read_file(path)
    return data

data = load_data("datasets/out.csv")
geo_data = load_data("datasets/provincias.geojson")

st.set_page_config(layout="wide")
st.title("Estudio demográfico en España")

tab1, tab2, tab3, tab4 = st.tabs(["Evolución de los fenómenos demográficos en España", "Relaciones entre los fenómenos demográficos", "Patrones de género en los fenómenos demográficos", "Resumen espacial"])

with tab1:
    st.header("Evolución temporal de los fenómenos demográficos en España")
    col1, col2 = st.columns(2)
    

    with col1:
        selected_metric = st.selectbox(
            "Seleccione la métrica que desee:",
            ("Delitos", "Nacimientos", "Defunciones", "Poblacion")
        )
        chart1 = createTemporalEvolutionProvincesChart(data, selected_metric)
        st.altair_chart(chart1, use_container_width=True)
    with col2:
        chart2 = createTemporalEvolutionChart(data)
        st.altair_chart(chart2, use_container_width=True)
    
    chart3 = createPopulationGrowthChart(data)
    st.altair_chart(chart3, use_container_width=True)
    
with tab2:
    st.header("Relación de los delitos con otros fenómenos demográficos en España")
    
    selected_metric = st.selectbox(
        "Seleccione la relación:",
        ("Tasa de criminalidad-Poblacion", "Tasa de criminalidad-Defunciones")
    )
    
    feature1, feature2 = selected_metric.split("-")
    
    chart4 = createCrimesCorrelationChart(data, feature1, feature2)
    st.altair_chart(chart4, use_container_width=True)

with tab3:
    
    selected_metric = st.selectbox(
        "Seleccione la métrica deseada:",
        ("Delitos", "Nacimientos", "Defunciones", "Poblacion")
    )
    
    chart5 = createSexAccumulatedChart(data, selected_metric)
    st.altair_chart(chart5, use_container_width=True)
    
    chart6 = createSexPieChart(data, selected_metric)
    st.altair_chart(chart6, use_container_width=True)

with tab4:
    selected_metric = st.selectbox(
        "Seleccione la métrica que desee visualizar en el mapa:",
        ("Poblacion", "Nacimientos", "Defunciones", "Delitos", "Tasa de natalidad", "Tasa de mortalidad", "Tasa de criminalidad")
    )
    fig = create_matplotlib_map(data, geo_data, selected_metric)
    st.pyplot(fig)