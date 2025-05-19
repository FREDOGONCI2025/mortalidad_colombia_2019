""" 
Análisis de Mortalidad en Colombia - Año 2019
---------------------------------------------

Este proyecto construye una aplicación web interactiva usando Dash y Plotly para visualizar patrones de mortalidad
en Colombia durante el año 2019. Integra múltiples visualizaciones que permiten explorar el comportamiento de las
muertes según departamento, municipio, causas, edad, sexo y temporalidad.

Autor: Ing. Héctor A. González Cifuentes
Fecha: Mayo 2025
"""

# ------------------- Importar librerías -------------------
import pandas as pd
import json
from dash import Dash, html, dcc, dash_table
import plotly.express as px
import os

# ------------------- Cargar datos -------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")


# Datos de mortalidad
df_muertes = pd.read_excel(os.path.join(DATA_DIR,"Anexo1.NoFetal2019_CE_15-03-23.xlsx"), engine="openpyxl")
df_muertes["COD_DANE"] = df_muertes["COD_DANE"].astype(str).str.zfill(6)
df_muertes["COD_MUERTE"] = df_muertes["COD_MUERTE"].astype(str).str.strip().str.upper()

# División político-administrativa
df_divipola = pd.read_excel(os.path.join(DATA_DIR,"Anexo3.Divipola_CE_15-03-23.xlsx"), engine="openpyxl")
df_divipola["COD_DANE"] = df_divipola["COD_DANE"].astype(str).str.zfill(6)

# Códigos de muerte
df_codigos = pd.read_excel(os.path.join(DATA_DIR,"Anexo2.CodigosDeMuerte_CE_15-03-23.xlsx"), engine="openpyxl", sheet_name="Final")
df_codigos["COD_MUERTE"] = df_codigos["COD_MUERTE"].astype(str).str.strip().str.upper()
df_codigos["DESCRIPCION_MUERTE"] = df_codigos["DESCRIPCION_MUERTE"].astype(str).str.strip()

# ------------------- Total por Departamento (Mapa) -------------------

df_total_muertes = df_muertes.groupby("COD_DEPARTAMENTO").size().reset_index(name="TotalMuertes")

df_departamentos = df_divipola[["COD_DEPARTAMENTO", "DEPARTAMENTO"]].drop_duplicates()
df_departamentos.rename(columns={"COD_DEPARTAMENTO": "COD_DEPTO", "DEPARTAMENTO": "NOMBRE"}, inplace=True)

df_total_muertes.rename(columns={"COD_DEPARTAMENTO": "COD_DEPTO"}, inplace=True)
df_mapa = pd.merge(df_total_muertes, df_departamentos, on="COD_DEPTO", how="left")
df_mapa["NOMBRE"] = df_mapa["NOMBRE"].str.strip().str.upper()

df_mapa["NOMBRE"] = df_mapa["NOMBRE"].replace({
    "ARCHIPIELAGO DE SAN ANDRES PROVIDENCIA Y SANTA CATALINA": "SAN ANDRÉS Y PROVIDENCIA",
    "BOGOTA D.C.": "BOGOTÁ D.C.",
    "VALLE": "VALLE DEL CAUCA"
})


with open(os.path.join(DATA_DIR,"colombia_departamentos.geojson"), "r", encoding="utf-8") as f:
    geojson_departamentos = json.load(f)

for feature in geojson_departamentos["features"]:
    feature["properties"]["NOMBRE_DPT"] = feature["properties"]["NOMBRE_DPT"].strip().upper()

# ------------------- Gráfico de líneas mensual -------------------
df_muertes["FECHA_DEFUNCION"] = pd.to_datetime({
    "year": df_muertes["AÑO"],
    "month": df_muertes["MES"],
    "day": 1
}, errors="coerce")

df_mensual = df_muertes.groupby(df_muertes["FECHA_DEFUNCION"].dt.to_period("M")).size().reset_index(name="TotalMuertes")
df_mensual["FECHA_DEFUNCION"] = df_mensual["FECHA_DEFUNCION"].dt.to_timestamp()

# ------------------- Gráfico de barras: ciudades más violentas -------------------
df_homicidios = df_muertes[df_muertes["COD_MUERTE"].str.startswith("X95")]
df_municipios = df_divipola[["COD_DANE", "MUNICIPIO"]].drop_duplicates()
df_homicidios = pd.merge(df_homicidios, df_municipios, on="COD_DANE", how="left")
df_top5 = df_homicidios.groupby("MUNICIPIO").size().reset_index(name="TotalHomicidios")
df_top5 = df_top5.sort_values(by="TotalHomicidios", ascending=False).head(5)

# ------------------- Gráfico circular -------------------
df_ciudades = df_muertes.groupby("COD_DANE").size().reset_index(name="TotalMuertes")
df_ciudades = pd.merge(df_ciudades, df_municipios, on="COD_DANE", how="left")
df_ciudades["MUNICIPIO"] = df_ciudades["MUNICIPIO"].str.upper()
df_menor_mortalidad = df_ciudades.sort_values(by="TotalMuertes", ascending=True).head(10)

# ------------------- Tabla: Principales causas -------------------
df_causas = df_muertes.groupby("COD_MUERTE").size().reset_index(name="Total")
df_causas = pd.merge(df_causas, df_codigos[["COD_MUERTE", "DESCRIPCION_MUERTE"]], on="COD_MUERTE", how="left")
df_top_causas = df_causas.sort_values(by="Total", ascending=False).head(10)

# ------------------- Histograma: Distribución por edad -------------------
bins = list(range(0, 86, 5)) + [150]
labels = [f"{i}-{i+4}" for i in range(0, 85, 5)] + ["85+"]

df_muertes["EDAD_GRUPO"] = pd.cut(df_muertes["GRUPO_EDAD1"], bins=bins, labels=labels, right=False)
df_edades = df_muertes["EDAD_GRUPO"].value_counts().sort_index().reset_index()
df_edades.columns = ["RangoEdad", "TotalMuertes"]

# ------------------- Gráfico de barras apiladas por sexo y departamento -------------------
df_sexo_dep = df_muertes.groupby(["COD_DEPARTAMENTO", "SEXO"]).size().reset_index(name="TotalMuertes")
df_sexo_dep = pd.merge(df_sexo_dep, df_departamentos, left_on="COD_DEPARTAMENTO", right_on="COD_DEPTO", how="left")
df_sexo_dep["SEXO"] = df_sexo_dep["SEXO"].map({1: "Masculino", 2: "Femenino", 9: "Sin especificar"})

# ------------------- Visualizaciones -------------------
fig_mapa = px.choropleth(df_mapa, geojson=geojson_departamentos, locations="NOMBRE",
    featureidkey="properties.NOMBRE_DPT", color="TotalMuertes",
    color_continuous_scale="Reds", projection="mercator",
    title="Total de muertes por departamento en Colombia (2019)", height=600)
fig_mapa.update_geos(fitbounds="locations", visible=False)
fig_mapa.update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 0})

fig_lineas = px.line(df_mensual, x="FECHA_DEFUNCION", y="TotalMuertes",
    title="Evolución mensual de muertes en Colombia (2019)", markers=True,
    labels={"FECHA_DEFUNCION": "Fecha", "TotalMuertes": "Número de muertes"}, height=400)
fig_lineas.update_layout(xaxis=dict(dtick="M1", tickformat="%b"))

fig_barras = px.bar(df_top5, x="MUNICIPIO", y="TotalHomicidios",
    title="Top 5 ciudades más violentas por homicidios (código X95)",
    labels={"MUNICIPIO": "Ciudad", "TotalHomicidios": "Homicidios por arma de fuego"},
    color="TotalHomicidios", color_continuous_scale="Reds", height=400)

fig_pie = px.pie(df_menor_mortalidad, names="MUNICIPIO", values="TotalMuertes",
    title="Top 10 ciudades con menor índice de mortalidad (2019)", height=400)

fig_histograma = px.bar(df_edades, x="RangoEdad", y="TotalMuertes",
    title="Distribución de muertes por rangos de edad (2019)",
    labels={"RangoEdad": "Rango de Edad", "TotalMuertes": "Número de muertes"}, height=400)

fig_barras_apiladas = px.bar(df_sexo_dep, x="NOMBRE", y="TotalMuertes", color="SEXO",
    title="Comparación del total de muertes por sexo en cada departamento (2019)",
    labels={"NOMBRE": "Departamento", "TotalMuertes": "Número de muertes"},
    barmode="stack", height=500)
fig_barras_apiladas.update_layout(xaxis_tickangle=-45)

# ------------------- Aplicación Dash -------------------

app = Dash(__name__)
server = app.server
app.layout = html.Div([
    html.H1("Análisis de Mortalidad - Colombia 2019", style={"textAlign": "center"}),

    html.H2("Distribución de muertes por departamento"),
    dcc.Graph(figure=fig_mapa),

    html.H2("Evolución mensual de muertes"),
    dcc.Graph(figure=fig_lineas),

    html.H2("Top 5 ciudades más violentas por homicidios"),
    dcc.Graph(figure=fig_barras),

    html.H2("Top 10 ciudades con menor índice de mortalidad"),
    dcc.Graph(figure=fig_pie),

    html.H2("Top 10 principales causas de muerte"),
    dash_table.DataTable(
        columns=[
            {"name": "Código", "id": "COD_MUERTE"},
            {"name": "Descripción", "id": "DESCRIPCION_MUERTE"},
            {"name": "Total", "id": "Total"},
        ],
        data=df_top_causas.to_dict("records"),
        style_table={"overflowX": "auto"},
        style_header={"backgroundColor": "lightgrey", "fontWeight": "bold"},
    ),

    html.H2("Distribución de muertes por edad"),
    dcc.Graph(figure=fig_histograma),

    html.H2("Comparación de muertes por sexo y departamento"),
    dcc.Graph(figure=fig_barras_apiladas)
])

# ------------------- Ejecutar -------------------
if __name__ == "__main__":
    app.run(debug=True)


