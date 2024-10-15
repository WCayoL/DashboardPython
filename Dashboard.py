import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go

# Leer el archivo CSV
data = pd.read_csv(r"C:\Users\Widdo\Desktop\sssssssssssssssssssss\IDP_SEPTIEMBRE_PRUEBA.csv", on_bad_lines='skip', delimiter=';')

# Calcular KPI por tienda
data['TotalByPlanogramm'] = data['sku_status'].apply(lambda x: 1 if x == 'by_planogramm' else 0)
data['TotalNotExposed'] = data['sku_status'].apply(lambda x: 1 if x == 'not_exposed' else 0)
data['TotalShelfError'] = data['sku_status'].apply(lambda x: 1 if x == 'shelf_error' else 0)
data['TotalSkuPositionError'] = data['sku_status'].apply(lambda x: 1 if x == 'sku_position_error' else 0)

# Agrupar por tienda y calcular el KPI
kpi_data = data.groupby('external_store_id').agg(
    TotalByPlanogramm=('TotalByPlanogramm', 'sum'),
    TotalNotExposed=('TotalNotExposed', 'sum'),
    TotalShelfError=('TotalShelfError', 'sum'),
    TotalSkuPositionError=('TotalSkuPositionError', 'sum')
).reset_index()

# Calcular el KPI de cumplimiento por tienda
kpi_data['KPI_Cumplimiento'] = kpi_data['TotalByPlanogramm'] / (
    kpi_data['TotalByPlanogramm'] + kpi_data['TotalNotExposed'] + kpi_data['TotalShelfError'] + kpi_data['TotalSkuPositionError'])

# Calcular KPI promedio
kpi_promedio = kpi_data['KPI_Cumplimiento'].mean()

# Crear gráfico de líneas para KPI por tienda
kpi_fig = go.Figure()

# Añadir la línea del KPI por tienda
kpi_fig.add_trace(go.Scatter(x=kpi_data['external_store_id'], 
                             y=kpi_data['KPI_Cumplimiento'] * 100,  # Convertir a porcentaje
                             mode='lines+markers', 
                             name='KPI por Tienda',
                             text=kpi_data.apply(lambda row: f"Tienda: {row['external_store_id']}<br>KPI: {row['KPI_Cumplimiento']*100:.2f}%", axis=1),  # Mostrar el ID de la tienda y el KPI
                             hovertemplate='%{text}'))  # Mostrar tienda y KPI con formato

# Añadir la línea del KPI promedio
kpi_fig.add_trace(go.Scatter(x=kpi_data['external_store_id'], 
                             y=[kpi_promedio * 100] * len(kpi_data),  # Convertir a porcentaje
                             mode='lines', 
                             name='KPI Promedio', 
                             line=dict(dash='dash'),
                             text=[f"KPI Promedio: {kpi_promedio * 100:.2f}%" for _ in range(len(kpi_data))],  # Mostrar KPI promedio
                             hovertemplate='%{text}'))  # Mostrar KPI promedio con formato

# Configurar el layout del gráfico
kpi_fig.update_layout(title='Rendimiento KPI por Tienda',
                      xaxis_title='ID de Tienda',
                      yaxis_title='KPI de Cumplimiento (%)',  # Mostrar el eje Y como porcentaje
                      showlegend=True)

# Configurar la aplicación Dash
app = Dash(__name__)

app.layout = html.Div(children=[
    html.Div([
        # Imagen del logo en la parte superior izquierda
        html.Img(src='/assets/retailatam.png', style={'height': '100px', 'float': 'left', 'margin-right': '20px'}),
        
        # Título del dashboard
        html.H1(children='', style={'display': 'inline-block', 'color': 'white'}),
        
        # Tarjeta de KPI y selector de tienda a la derecha
        html.Div([
            # Selector de tienda
            dcc.Dropdown(
                id='tienda-selector',
                options=[{'label': f'Tienda {store_id}', 'value': store_id} for store_id in kpi_data['external_store_id']],
                value=None,  # Valor inicial
                placeholder="Selecciona una tienda",
                style={'width': '150px', 'margin-right': '10px'}
            ),

            # Tarjeta de KPI
            html.Div(id='kpi-tarjeta', style={
                'backgroundColor': 'white', 
                'borderRadius': '10px', 
                'padding': '20px', 
                'textAlign': 'center', 
                'fontSize': '24px',
                'boxShadow': '0 4px 8px 0 rgba(0,0,0,0.2)',
                'width': '150px'
            })
        ], style={'display': 'flex', 'align-items': 'center', 'margin-left': 'auto'})  # Alinear a la derecha
    ], style={'display': 'flex', 'align-items': 'center', 'backgroundColor': '#332F2C', 'padding': '20px'}),

    # Gráfico del KPI en el centro
    dcc.Graph(
        id='kpi-grafico',
        figure=kpi_fig,
    )
], style={'height': '100vh', 'padding': '0px'})  # Remover padding de la parte superior para el gráfico


# Actualizar el KPI en la tarjeta cuando se selecciona una tienda
@app.callback(
    Output('kpi-tarjeta', 'children'),
    [Input('tienda-selector', 'value')]
)
def actualizar_kpi_tarjeta(tienda_seleccionada):
    if tienda_seleccionada is None:
        # Mostrar el KPI promedio si no se selecciona ninguna tienda
        return f'KPI Promedio: {kpi_promedio * 100:.2f}%'
    else:
        # Mostrar el KPI de la tienda seleccionada
        kpi_tienda = kpi_data[kpi_data['external_store_id'] == tienda_seleccionada]['KPI_Cumplimiento'].values[0]
        return f'KPI Tienda {tienda_seleccionada}: {kpi_tienda * 100:.2f}%' 


# Ejecutar la aplicación
if __name__ == '__main__':
    app.run_server(debug=True)
