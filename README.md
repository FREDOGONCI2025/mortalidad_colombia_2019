# Análisis de Mortalidad en Colombia - 2019

Esta aplicación web interactiva, desarrollada con Python y Dash, permite explorar visualmente los patrones de mortalidad en Colombia durante el año 2019.

## Estructura del Proyecto

```
mortalidad_app/
├── src/
│   ├── app.py
│   ├── requirements.txt
│   ├── render.yaml
├── data/
│   ├── Anexo1.NoFetal2019_CE_15-03-23.xlsx
│   ├── Anexo2.CodigosDeMuerte_CE_15-03-23.xlsx
│   ├── Anexo3.Divipola_CE_15-03-23.xlsx
│   └── colombia_departamentos.geojson
└── README.md 

```
## Visualizaciones Incluidas

1. **Mapa**: Muertes por departamento.
2. **Línea**: Muertes mensuales.
3. **Barras**: Ciudades con más homicidios (X95).
4. **Circular**: Ciudades con menor mortalidad.
5. **Tabla**: Principales causas de muerte.
6. **Histograma**: Distribución por edades.
7. **Barras Apiladas**: Muertes por sexo en departamentos.

## Requisitos

- Python 3.11
- Dash 3.0.4
- Plotly 6.1.0
- Pandas 2.2.3
- OpenPyXL 3.1.5
- Gunicorn 23.0.0
- Ver `requirements.txt` para dependencias adicionales

## Cómo ejecutar

Desde la carpeta raíz del proyecto:

```bash
cd src
python app.py
```

## Despliegue en Render

La aplicación puede desplegarse como servicio web gratuito utilizando la configuración proporcionada en `render.yaml`.

---

**Autor**: Héctor A. González Cifuentes  
**Fecha**: Mayo 2025