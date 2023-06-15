#IMPORTANTE! Para executar o código, é necessário instalar as bibliotecas abaixo:
#pip install dash
#pip pandas
#pip install plotly
import math
import pandas as pd
import dash
from dash import dcc
from dash import html
from dash import dash_table
import plotly.graph_objects as go

#Cálculo do dia juliano:
d =  30
m =  5
y =  1999
horas = 19
minutos = 0

t = math.floor(367 * y - math.floor((7 *(y + math.floor((m+9)/12)))/4) + 
               math.floor((275*m)/9) + d - 730530)
t += ((horas/24) + (minutos/1440))

#Abaixo, estão as funções utilizadas para o cálculo dos elementos orbitais e coordenadas dos planetas:

#Se eu não me engano, numpy já tem essas funções, mas optei por criar as minhas.
#Função para converter graus para radianos:
def deg2rad(theta):
  return(theta*math.pi/180)

#Função para converter radianos para graus:
def rad2deg(theta):
  return(theta*180/math.pi)

#Função para cálculo de anomalia excêntrica (E):
def calcularAnomaliaE(anomaliaMedia, anomaliaEAprox, e):
    delta_E = ((anomaliaMedia - anomaliaEAprox + e * math.sin(anomaliaEAprox)) /
               (1 - e * math.cos(anomaliaEAprox)))
    E = anomaliaEAprox + delta_E

    if abs(delta_E) > 5e-6:
        anomaliaEAprox = E
        delta_E = ((anomaliaMedia - anomaliaEAprox + e * math.sin(anomaliaEAprox)) /
                    (1 - e * math.cos(anomaliaEAprox)))
        E = anomaliaEAprox + delta_E
        return round(E, 3)
    else:
        return round(E, 3)

#Função para cálculo da anomalia verdadeira (v):
def calcularAnomaliaV(e, E):
    v = 2 * (math.atan((math.sqrt((1+e)/(1-e)))*math.tan(E/2)))
    return round(v, 3)

#Função para cálculo da distância do planeta ao Sol:
def calcularR (alfa, e, v):
    au = 149597870700
    r = ((alfa * (1 - e**2)) / (1 + (e * math.cos(v))))
    return r

#Função para cálculo das coordenadas cartesianas:
def calcularCoordenadasCart(r, longitudeNodo, argumentoPerielio, v, i):
    km = 1000
    x = (r * (math.cos(longitudeNodo)*math.cos(argumentoPerielio + v) - math.sin(longitudeNodo)*math.sin(argumentoPerielio+v)*math.cos(i))) / km
    y = (r * (math.sin(longitudeNodo)*math.cos(argumentoPerielio + v) + math.cos(longitudeNodo)*math.sin(argumentoPerielio+v)*math.cos(i))) / km
    z = (r * math.sin(argumentoPerielio + v)*math.sin(i)) / km
    return x, y, z

#Função para cálculo das coordenadas eclípticas heliocêntricas:
#Um conceito muito interessante aplicado na prática, aninhamento de funções.
def calcularCoordenadasEclip(x, y, z):
    lambda1 = math.atan(y/x) 
    beta1 = math.atan(z/(math.sqrt(x**2+y**2)))
    lambda1 = rad2deg(lambda1)
    beta1 = rad2deg(beta1)
    if lambda1 < 0:
        lambda1 += 360
        return lambda1, beta1
    else:
        return lambda1, beta1

#Função para adicionar planetass dentro do Dataframe elementos orbitais:
elementosOrbitaisdf = pd.DataFrame(columns=['Planeta', 'Ω (°)', 'i (°)', 'Π (°)', 'α (ua)', 'e', 'M (°)', 'E (°)', 'ν (°)', 'r (ua)'])
def adicionarElementos(elementosOrbitaisdf, planeta, longitudeNodo, i, argumentoPerielio, alfa, e, anomaliaMedia, E, v, r):
    novoRegistro = {'Planeta': planeta, 'Ω (°)': longitudeNodo, 'i (°)': i, 'Π (°)': argumentoPerielio, 'α (ua)': alfa, 'e': e, 'M (°)': anomaliaMedia, 'E (°)': E, 'ν (°)': v, 'r (ua)': r}
    elementosOrbitaisdf = pd.concat([elementosOrbitaisdf, pd.DataFrame(novoRegistro, index=[0])], ignore_index=True)
    return elementosOrbitaisdf

#Função para adicionar os planetas dentro do DataFrame coordenadas:
coordenadasdf = pd.DataFrame(columns=['Planeta', 'X (km)', 'Y (km)', 'Z (km)', 'l (°)', 'b (°)'])
def adicionarPlaneta(coordenadasdf, planeta, x, y, z, l, b):
    novoRegistro = {'Planeta': planeta, 'X (km)': x, 'Y (km)': y, 'Z (km)': z, 'l (°)':l, 'b (°)':b}
    coordenadasdf = pd.concat([coordenadasdf, pd.DataFrame(novoRegistro, index=[0])], ignore_index=True)
    return coordenadasdf

#Cálculo dos elementos orbitais e coordenadas dos planetas:
#Os comentários a seguir para mercúrio, vale para todos outros planetas.

#Mercúrio:
#Como o math utiliza apenas radianos, é necessário converter os valores de graus para radianos:
longitudeNodo = 48.3313 + 3.24587e-5 * t
longitudeNodo = deg2rad(longitudeNodo)
i = 7.0047 + 5.00e-8 * t
i = deg2rad(i)
argumentoPerielio = 29.1241 + 1.01444e-5 * t
argumentoPerielio = deg2rad(argumentoPerielio)
alfa = 0.387098 * 149597870700
e = 0.205635 + 5.59e-10 * t
anomaliaMedia = 168.6562 + 4.0923344368 * t
anomaliaMedia = deg2rad(anomaliaMedia)
anomaliaEAprox = anomaliaMedia

E = calcularAnomaliaE(anomaliaMedia, anomaliaEAprox, e)
v = calcularAnomaliaV(e, E)
r = calcularR(alfa, e, v)

x, y, z = calcularCoordenadasCart(r, longitudeNodo, argumentoPerielio, v, i)
l, b = calcularCoordenadasEclip(x, y, z)

#Conversão dos valores de radianos para graus e ajuste dos valores para o intervalo de 0 a 360:
longitudeNodo = rad2deg(longitudeNodo) % 360
i = rad2deg(i) % 360
argumentoPerielio = rad2deg(argumentoPerielio) % 360
anomaliaMedia = rad2deg(anomaliaMedia) % 360
E = E % (2 * math.pi)
E = rad2deg(E)
v = v % (2 * math.pi)
v = rad2deg(v)

#Adicionando os valores no DataFrame:
elementosOrbitaisdf = adicionarElementos(elementosOrbitaisdf, 'Mercúrio', longitudeNodo, i, argumentoPerielio, alfa, e, anomaliaMedia, E, v, r)
coordenadasdf = adicionarPlaneta(coordenadasdf, 'Mercúrio', x, y, z, l, b)

#Vênus:
longitudeNodo = 76.6799 + 2.46590e-5 * t
longitudeNodo = deg2rad(longitudeNodo % 360)
i = 3.3946 + 2.75e-8 * t
i = deg2rad(i % 360)
argumentoPerielio = 54.8910 + 1.38374e-5 * t
argumentoPerielio = deg2rad(argumentoPerielio % 360)
alfa = 0.723330 * 149597870700
e = 0.006773 - 1.302e-9 * t
anomaliaMedia = 48.0052 + 1.6021302244 * t
anomaliaMedia = deg2rad(anomaliaMedia % 360)
anomaliaEAprox = anomaliaMedia

E = calcularAnomaliaE(anomaliaMedia, anomaliaEAprox, e)
v = calcularAnomaliaV(e, E)
r = calcularR(alfa, e, v)

x, y, z = calcularCoordenadasCart(r, longitudeNodo, argumentoPerielio, v, i)
l, b = calcularCoordenadasEclip(x, y, z)

longitudeNodo = rad2deg(longitudeNodo)
i = rad2deg(i)
argumentoPerielio = rad2deg(argumentoPerielio)
anomaliaMedia = rad2deg(anomaliaMedia)
E = E % (2 * math.pi)
E = rad2deg(E)
v = v % (2 * math.pi)
v = rad2deg(v)

coordenadasdf = adicionarPlaneta(coordenadasdf, 'Vênus', x, y, z, l, b)
elementosOrbitaisdf = adicionarElementos(elementosOrbitaisdf, 'Vênus', longitudeNodo, i, argumentoPerielio, alfa, e, anomaliaMedia, E, v, r)


#Terra:
longitudeNodo = 0.0
i = 0.0
argumentoPerielio = 282.9404 + 4.70935e-5 * t
argumentoPerielio = deg2rad(argumentoPerielio % 360)
alfa = 1.000000 * 149597870700
e = 0.016709 - 1.151e-9 * t
anomaliaMedia = 356.0470 + 0.9856002585 * t
anomaliaMedia = deg2rad(anomaliaMedia % 360)
anomaliaEAprox = anomaliaMedia

E = calcularAnomaliaE(anomaliaMedia, anomaliaEAprox, e)
v = calcularAnomaliaV(e, E)
r = calcularR(alfa, e, v)

x, y, z = calcularCoordenadasCart(r, longitudeNodo, argumentoPerielio, v, i)
l, b = calcularCoordenadasEclip(x, y, z)

longitudeNodo = rad2deg(longitudeNodo)
i = rad2deg(i)
argumentoPerielio = rad2deg(argumentoPerielio)
anomaliaMedia = rad2deg(anomaliaMedia)
E = E % (2 * math.pi)  
E = rad2deg(E)
v = v % (2 * math.pi)
v = rad2deg(v)

coordenadasdf = adicionarPlaneta(coordenadasdf, 'Terra', x, y, z, l, b)
elementosOrbitaisdf = adicionarElementos(elementosOrbitaisdf, 'Terra', longitudeNodo, i, argumentoPerielio, alfa, e, anomaliaMedia, E, v, r)


#Marte:
longitudeNodo = 49.5574 + 2.11081e-5 * t
longitudeNodo = deg2rad(longitudeNodo % 360)
i = 1.8497 + 1.78e-8 * t
i = deg2rad(i % 360)
argumentoPerielio = 286.5016 + 2.92961e-5 * t
argumentoPerielio = deg2rad(argumentoPerielio % 360)
alfa = 1.523688 * 149597870700
e = 0.093405 + 2.516e-9 * t
anomaliaMedia = 18.6021 + 0.5240207766 * t
anomaliaMedia = deg2rad(anomaliaMedia % 360)
anomaliaEAprox = anomaliaMedia

E = calcularAnomaliaE(anomaliaMedia, anomaliaEAprox, e)
v = calcularAnomaliaV(e, E)
r = calcularR(alfa, e, v)

x, y, z = calcularCoordenadasCart(r, longitudeNodo, argumentoPerielio, v, i)
l, b = calcularCoordenadasEclip(x, y, z)

longitudeNodo = rad2deg(longitudeNodo)
i = rad2deg(i)
argumentoPerielio = rad2deg(argumentoPerielio)
anomaliaMedia = rad2deg(anomaliaMedia)
E = E % (2 * math.pi)
E = rad2deg(E)
v = v % (2 * math.pi)
v = rad2deg(v)

coordenadasdf = adicionarPlaneta(coordenadasdf, 'Marte', x, y, z, l, b)
elementosOrbitaisdf = adicionarElementos(elementosOrbitaisdf, 'Marte', longitudeNodo, i, argumentoPerielio, alfa, e, anomaliaMedia, E, v, r)


#Júpiter:
longitudeNodo = 100.4542 + 2.76854e-5 * t
longitudeNodo = deg2rad(longitudeNodo % 360)
i = 1.3030 + 1.557e-8 * t
i = deg2rad(i % 360)
argumentoPerielio = 273.8777 + 1.64505e-5 * t
argumentoPerielio = deg2rad(argumentoPerielio % 360)
alfa = 5.20256 * 149597870700
e = 0.048498 + 4.469e-9 * t
anomaliaMedia = 19.8950 + 0.0830853001 * t
anomaliaMedia = deg2rad(anomaliaMedia % 360)
anomaliaEAprox = anomaliaMedia

E = calcularAnomaliaE(anomaliaMedia, anomaliaEAprox, e)
v = calcularAnomaliaV(e, E)
r = calcularR(alfa, e, v)

x, y, z = calcularCoordenadasCart(r, longitudeNodo, argumentoPerielio, v, i)
l, b = calcularCoordenadasEclip(x, y, z)

longitudeNodo = rad2deg(longitudeNodo)
i = rad2deg(i)
argumentoPerielio = rad2deg(argumentoPerielio)
anomaliaMedia = rad2deg(anomaliaMedia)
E = E % (2 * math.pi)
E = rad2deg(E)
v = v % (2 * math.pi)
v = rad2deg(v)  

coordenadasdf = adicionarPlaneta(coordenadasdf, 'Júpiter', x, y, z, l, b)
elementosOrbitaisdf = adicionarElementos(elementosOrbitaisdf, 'Júpiter', longitudeNodo, i, argumentoPerielio, alfa, e, anomaliaMedia, E, v, r)


#Saturno:
longitudeNodo = 113.6634 + 2.38980e-5 * t
longitudeNodo = deg2rad(longitudeNodo % 360)
i = 2.4886 - 1.081e-7 * t
i = deg2rad(i % 360)
argumentoPerielio = 339.3939 + 2.97661e-5 * t
argumentoPerielio = deg2rad(argumentoPerielio % 360)
alfa = 9.55475 * 149597870700
e = 0.055546 - 9.499e-9 * t
anomaliaMedia = 316.9670 + 0.0334442282 * t
anomaliaMedia = deg2rad(anomaliaMedia % 360)
anomaliaEAprox = anomaliaMedia

E = calcularAnomaliaE(anomaliaMedia, anomaliaEAprox, e)
v = calcularAnomaliaV(e, E)
r = calcularR(alfa, e, v)

x, y, z = calcularCoordenadasCart(r, longitudeNodo, argumentoPerielio, v, i)
l, b = calcularCoordenadasEclip(x, y, z)

longitudeNodo = rad2deg(longitudeNodo)
i = rad2deg(i)
argumentoPerielio = rad2deg(argumentoPerielio)
anomaliaMedia = rad2deg(anomaliaMedia)
E = E % (2 * math.pi)
E = rad2deg(E)
v = v % (2 * math.pi)
v = rad2deg(v)  

coordenadasdf = adicionarPlaneta(coordenadasdf, 'Saturno', x, y, z, l, b)
elementosOrbitaisdf = adicionarElementos(elementosOrbitaisdf, 'Saturno', longitudeNodo, i, argumentoPerielio, alfa, e, anomaliaMedia, E, v, r)


#Urano:
longitudeNodo = 74.0005 + 1.3978e-5 * t
longitudeNodo = deg2rad(longitudeNodo % 360)
i = 0.7733 + 1.9e-8 * t
i = deg2rad(i % 360)
argumentoPerielio = 96.6612 + 3.0565e-5 * t
argumentoPerielio = deg2rad(argumentoPerielio % 360)
alfa = ((19.18171 - 1.55e-8 * t) * 149597870700)
e = 0.047318 + 7.45e-9 * t
anomaliaMedia = 142.5905 + 0.011725806 * t
anomaliaMedia = deg2rad(anomaliaMedia % 360)
anomaliaEAprox = anomaliaMedia

E = calcularAnomaliaE(anomaliaMedia, anomaliaEAprox, e)
v = calcularAnomaliaV(e, E)
r = calcularR(alfa, e, v)

x, y, z = calcularCoordenadasCart(r, longitudeNodo, argumentoPerielio, v, i)
l, b = calcularCoordenadasEclip(x, y, z)

longitudeNodo = rad2deg(longitudeNodo)
i = rad2deg(i)
argumentoPerielio = rad2deg(argumentoPerielio)
anomaliaMedia = rad2deg(anomaliaMedia)
E = E % (2 * math.pi)
E = rad2deg(E)
v = v % (2 * math.pi)
v = rad2deg(v)  

coordenadasdf = adicionarPlaneta(coordenadasdf, 'Urano', x, y, z, l, b)
elementosOrbitaisdf = adicionarElementos(elementosOrbitaisdf, 'Urano', longitudeNodo, i, argumentoPerielio, alfa, e, anomaliaMedia, E, v, r)


#Netuno:
longitudeNodo = 131.7806 + 3.0173e-5 * t
longitudeNodo = deg2rad(longitudeNodo % 360)
i = 1.7700 - 2.55e-7 * t
i = deg2rad(i % 360)
argumentoPerielio = 272.8461 - 6.027e-6 * t
argumentoPerielio = deg2rad(argumentoPerielio % 360)
alfa = ((30.05826 - 3.313e-8 * t) * 149597870700)
e = 0.008606 + 2.15e-9 * t
anomaliaMedia = 260.2471 + 0.005995147 * t
anomaliaMedia = deg2rad(anomaliaMedia % 360)
anomaliaEAprox = anomaliaMedia

E = calcularAnomaliaE(anomaliaMedia, anomaliaEAprox, e)
v = calcularAnomaliaV(e, E)
r = calcularR(alfa, e, v)

x, y, z = calcularCoordenadasCart(r, longitudeNodo, argumentoPerielio, v, i)
l, b = calcularCoordenadasEclip(x, y, z)

longitudeNodo = rad2deg(longitudeNodo)
i = rad2deg(i)
argumentoPerielio = rad2deg(argumentoPerielio)
anomaliaMedia = rad2deg(anomaliaMedia)
E = E % (2 * math.pi)
E = rad2deg(E)
v = v % (2 * math.pi)
v = rad2deg(v)  

coordenadasdf = adicionarPlaneta(coordenadasdf, 'Netuno', x, y, z, l, b)
elementosOrbitaisdf = adicionarElementos(elementosOrbitaisdf, 'Netuno', longitudeNodo, i, argumentoPerielio, alfa, e, anomaliaMedia, E, v, r)

#Ajustando as casas decimais:
ua = 149597870700
elementosOrbitaisdf['Ω (°)'] = elementosOrbitaisdf['Ω (°)'].round(3)
elementosOrbitaisdf['i (°)'] = elementosOrbitaisdf['i (°)'].round(3)
elementosOrbitaisdf['Π (°)'] = elementosOrbitaisdf['Π (°)'].round(3)
elementosOrbitaisdf['α (ua)'] = (elementosOrbitaisdf['α (ua)']/ua).round(3)
elementosOrbitaisdf['e'] = elementosOrbitaisdf['e'].round(3)
elementosOrbitaisdf['M (°)'] = elementosOrbitaisdf['M (°)'].round(3)
elementosOrbitaisdf['E (°)'] = elementosOrbitaisdf['E (°)'].round(3)
elementosOrbitaisdf['ν (°)'] = elementosOrbitaisdf['ν (°)'].round(3)
elementosOrbitaisdf['r (ua)'] = (elementosOrbitaisdf['r (ua)']/ua).round(3)

coordenadasdf['X (km)'] = coordenadasdf['X (km)'].round(0)
coordenadasdf['Y (km)'] = coordenadasdf['Y (km)'].round(0)
coordenadasdf['Z (km)'] = coordenadasdf['Z (km)'].round(0)
coordenadasdf['l (°)'] = coordenadasdf['l (°)'].round(3)
coordenadasdf['b (°)'] = coordenadasdf['b (°)'].round(3)

#Seção focada no cálculo do baricentro do sistema solar:

#Criando um dataframe com as massas citadas no texto explicativo:
data = [
    {'Objeto': 'Mercúrio', 'Massa (kg)': 3.3011e23},
    {'Objeto': 'Vênus', 'Massa (kg)': 4.8675e24},
    {'Objeto': 'Terra', 'Massa (kg)': 5.9722e24},
    {'Objeto': 'Marte', 'Massa (kg)': 6.4171e23},
    {'Objeto': 'Júpiter', 'Massa (kg)': 1.8981e27},
    {'Objeto': 'Saturno', 'Massa (kg)': 5.6834e26},
    {'Objeto': 'Urano', 'Massa (kg)': 8.6810e25},
    {'Objeto': 'Netuno', 'Massa (kg)': 1.0241e26},
    {'Objeto': 'Sol', 'Massa (kg)': 1.9885e30}
]
#Criando um dataframe com as massas dos planetas:
massadf = pd.DataFrame(data)
#Calculando a massa total do sistema solar:
massaTotal = massadf['Massa (kg)'].sum()
#Criando um array com as massas dos planetas:
massas = massadf['Massa (kg)'].values

#Adicionando as coordenadas do Sol ao dataframe:
dados_sol = {'Planeta': 'Sol', 'X (km)': 0, 'Y (km)': 0, 'Z (km)': 0, 'l (°)': 0, 'b (°)': 0}
coordenadasdf = pd.concat([coordenadasdf, pd.DataFrame(dados_sol, index=[0])], ignore_index=True)
Xk = coordenadasdf['X (km)'].values
Yk = coordenadasdf['Y (km)'].values
Zk = coordenadasdf['Z (km)'].values

#Calculando o baricentro do sistema solar:
Xcm = 0
Ycm = 0
Zcm = 0

#Calculando as coordenadas do baricentro para cada eixo:
for index, row in coordenadasdf.iterrows():
    Xcm += (massas[index] * Xk[index])
    Ycm += (massas[index] * Yk[index])
    Zcm += (massas[index] * Zk[index])

Xcm = Xcm / massaTotal
Ycm = Ycm / massaTotal
Zcm = Zcm / massaTotal

deltakm = math.sqrt(Xcm**2 + Ycm**2 + Zcm**2)
delta = deltakm / 696340

#Criando um dataframe com as coordenadas do baricentro:
baricentro = {
    'Xcm (km)': [round(Xcm, 3)],
    'Ycm (km)': [round(Ycm, 3)],
    'Zcm (km)': [round(Zcm, 3)],
    '∆ (km)': [round(deltakm, 3)],
    '∆' : [round(delta, 3)],
    '?Fora ou dentro?': ['Fora' if delta > 1 else 'Dentro']
}

baricentrodf = pd.DataFrame(baricentro)

coordenadasdf = coordenadasdf[coordenadasdf['Planeta'] != 'Sol']

#Módulo focado na configuração Dashboard:
#Criação do app:
app = dash.Dash(__name__)

#Criação do gráfico polar:
fig = go.Figure(data=go.Scatterpolar(r = [1, 2, 3, 4, 5, 6, 7, 8], theta = coordenadasdf['l (°)'].tolist(), mode = 'markers',))

#Configuração do layout do gráfico polar:
fig.update_layout(
    polar=dict(
        bgcolor='lightblue', 
        radialaxis=dict(visible=True),
        domain=dict(x=[0.1, 0.9], y=[0, 1])
    ),
    paper_bgcolor='lightgray'
)

#Criação do layout do app (HTML):
app.layout = html.Div(
    style={"background-color": "lightgray", "padding": "20px"},
    children=[
        html.H1("FIS02015 – Trabalho 1: Cálculo dos Elementos Orbitais"),
        html.Div(
            children=[
                html.Table(
                    children=[
                        html.Tr(
                            children=[
                                html.Td(["Nome: ", html.Strong("Gregory Fiel")]),
                                html.Td(["Cartão: ", html.Strong("00323639")])
                            ]   #Tabela das minhas informações
                        ),
                        html.Tr(
                            children=[
                                html.Td(["Data: ", html.Strong("30/05/1999")]),
                                html.Td(["Hora: ", html.Strong("19:00")])
                            ]   #Tabela da data e hora do cálculo
                        )
                    ],
                    style={"border": "1px solid black"}
                ),
                html.H2("Elementos orbitais:"),
                dash_table.DataTable(
                    data=elementosOrbitaisdf.to_dict('records'),
                    columns=[{'name': col, 'id': col} for col in elementosOrbitaisdf.columns],
                    style_table={'border': '1px solid black'},
                    style_header={'fontWeight': 'bold'},
                    style_cell={
                        'textAlign': 'left',
                        'whiteSpace': 'normal',
                        'overflow': 'hidden',
                        'textOverflow': 'ellipsis'
                    },
                    style_cell_conditional=[
                        {'if': {'column_id': col}, 'textAlign': 'right'}
                        for col in elementosOrbitaisdf.columns[1:]
                    ] #Tabela dos elementos orbitais
                ),
                html.H2("Coordenadas retangulares e coordenadas eclípticas:"),
                dash_table.DataTable(
                    data=coordenadasdf.to_dict('records'),
                    columns=[{'name': col, 'id': col} for col in coordenadasdf.columns],
                    style_table={'border': '1px solid black'},
                    style_header={'fontWeight': 'bold'},
                    style_cell={
                        'textAlign': 'left',
                        'whiteSpace': 'normal',
                        'overflow': 'hidden',
                        'textOverflow': 'ellipsis'
                    },
                    style_cell_conditional=[
                        {'if': {'column_id': col}, 'textAlign': 'right'}
                        for col in coordenadasdf.columns[1:]
                    ]   #Tabela das coordenadas retangulares e eclípticas
                ),
                html.H2("Baricentro do Sistema Solar:"),
                dash_table.DataTable(
                    data=baricentrodf.to_dict('records'),
                    columns=[{'name': col, 'id': col} for col in baricentrodf.columns],
                    style_table={'border': '1px solid black'},
                    style_header={'fontWeight': 'bold'},
                    style_data={'text-align': 'right'},
                    style_cell={
                        'whiteSpace': 'normal',
                        'overflow': 'hidden',
                        'textOverflow': 'ellipsis'
                    }  #Tabela do baricentro do sistema solar
                ),
                html.H2("Posições angulares dos planetas:"),
                html.Ul([
                    html.Li("1 Mercúrio"),
                    html.Li("2 Vênus"),
                    html.Li("3 Terra"),
                    html.Li("4 Marte"),
                    html.Li("5 Júpiter"),
                    html.Li("6 Saturno"),
                    html.Li("7 Urano"),
                    html.Li("8 Netuno")
                ]), #Lista dos planetas
                dcc.Graph(figure=fig, style={"width": "100%", "height": "600px"}) #Gráfico polar
            ]
        )
    ]
)

#Execução do app:
if __name__ == "__main__":
    app.run_server(debug=True) #debug=True para atualizar automaticamente o app quando o código for alterado

#Se o app não abrir automaticamente, acesse o link: http://127.0.0.1:8050/

#Seção para meus comentários:
#Não sei muito sobre html, então optei por fazer o layout mais simples possível, com tabelas, listas e um gráfico polar.
#Dash é uma biblioteca muito interessante, junto com o plotly, que permite a criação de gráficos interativos e que parecer ser um power BI mais simples.
#O próprio site da plotly tem uma documentação muito boa, com exemplos de gráficos e códigos para a criação deles. https://plotly.com/examples/
#O site do Dash também tem uma documentação muito boa, com exemplos de layouts e códigos para a criação deles. https://dash.plotly.com/layout, onde acabei me baseando para criar o layout do app.
#Infelizmente não tive muito tempo para a elaboração do app no geral, gostaria de ter usado um módulo chamado dbc, que permite a criação de layouts mais complexos, com mais elementos, como botões, caixas de texto, etc, programando pouco.
#Preferi fazer várias funções para os cálculos, para que o código ficasse mais organizado e mais fácil de entender. Acaba sendo tudo muito repetitivo, e seria mais fácil errar.
