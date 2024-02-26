import pandas as pd
import plotly.express as px
import streamlit as st
from database.maturity import get_ind


st.set_page_config(layout='wide', page_icon='icon.jpeg', page_title='Maturidade de Governança de Dados')
df = pd.read_excel('autodiagnostico.xlsx')
# Buscando dados dos Itens
itens = get_ind()

def pagina_inicio():
    st.title('Avaliação de Maturidade de Dados')
    st.write(
        'Este projeto visa avaliar e acompanhar o nível de maturidade da governança de dados em diferentes organizações.')
    st.subheader('Métricas da Estrutura:')

    eixo = st.sidebar.selectbox("Eixo", itens['eixo'].unique())
    df_filtered = itens[itens['eixo'] == eixo]

    cola, colb, colc, cold  = st.columns(4)
    col3, col4 = st.columns(2)

    cola.metric('Eixo', itens['eixo'].nunique())
    colb.metric('Tópicos', itens['topico'].nunique())
    colc.metric('Itens', itens['item'].count())
    cold.metric('Níveis', 5)

    df_eixo = itens.groupby('eixo')['item'].count().reset_index()
    fig_pie = px.pie(df_eixo, values='item', names='eixo', title='Eixos da Infraestrutura Nacional de Dados', hole=0.5)
    fig_pie.update_traces(textinfo='percent + value')
    col3.plotly_chart(fig_pie, use_container_width=True)

    df_topico = df_filtered.groupby('topico')['item'].count().reset_index()
    fig_pie_tp = px.pie(df_topico, values='item', names='topico', title=f'Tópicos da Maturidade - {eixo}', hole=0.5)
    fig_pie_tp.update_traces(textinfo='percent + value')
    col4.plotly_chart(fig_pie_tp, use_container_width=True)


    # Listar os tópicos avaliados
    st.markdown("### Itens de Maturidade de Dados")
    st.write("Aqui está uma breve descrição dos Itens de Maturidade de Dados.")
    st.dataframe(df_filtered, column_order=['linha','item','topico','eixo'])


# Exibir a imagem redimensionada
#st.image('dedad.png', caption='Departamento de Infraestrutura de Dados')

def autodiagnostico():
    st.title('Autodiagnóstico da Maturidade de Dados')
    st.write(
        'Este projeto visa avaliar e acompanhar o nível de maturidade da governança de dados em diferentes organizações.')
    st.subheader('Métricas de desempenho:')

    grupo = st.sidebar.selectbox("Grupo", df['GRUPO'].unique())
    df_filtered = df[df['GRUPO'] == grupo]

    cola, colb, colc, cold = st.columns(4)
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    cola.metric('Grupo', df['GRUPO'].nunique())
    colb.metric('Órgãos', df['ORGAO'].nunique())
    colc.metric('Média Geral', df['NIVEL'].mean().round(0))
    cold.metric('Itens', itens['item'].count())

    # Gráfico Barra Geral
    fig_data_total = px.bar(df, x='SIGLA', y='NIVEL', color='Ranking', title='Maturidade de Dados - Geral', text='ORGAO')
    col1.plotly_chart(fig_data_total, use_container_width=True)

    # Gráfico Barra por Grupo
    fig_data_por_grupo = px.bar(df_filtered, x='SIGLA', y='NIVEL', color='Ranking', title=f'Maturidade de Dados - {grupo.title()}', text='ORGAO')
    col2.plotly_chart(fig_data_por_grupo, use_container_width=True)

    # Gráfico Barra Média por Grupo
    df_grupo = df.groupby('GRUPO')['NIVEL'].mean().reset_index().round(2)
    colors = ['< 2' if media < 2 else '> 2' for media in df_grupo['NIVEL']]
    fig_grupo = px.bar(df_grupo, x='GRUPO', y='NIVEL', title='Média por Grupo', color=colors, color_discrete_map={True: 'red'}, height=500, width=600)
    col3.plotly_chart(fig_grupo)

    # Gráfico Pizza Média Itens
    indices_colunas = list(range(7, 44))  # Selecionando as colunas de 5 a 14
    df_topicos = df_filtered.iloc[:, indices_colunas]
    medias_topicos = df_topicos.mean().round(2)
    df_medias = pd.DataFrame({'Tópicos': medias_topicos.index, 'Médias': medias_topicos.values})
    fig_pizza = px.pie(df_medias, values='Médias', names='Tópicos', title=f'Médias dos Tópicos - {grupo.title()}', height=600, width=800)
    fig_pizza.update_traces(textinfo='value')
    col4.plotly_chart(fig_pizza)

    st.markdown("### Dados do Grupo")
    st.write("Aqui está uma breve descrição do DataFrame.")
    st.dataframe(df_filtered)
def instituicoes():
    st.title('Análise Individual')
    st.write('Teste!')


    # Criar um DataFrame de exemplo
    data = {
        'Categoria': ['A', 'B', 'C', 'D', 'E'],
        'Valor1': [4, 3, 2, 5, 4],
        'Valor2': [3, 2, 3, 4, 5],
        'Valor3': [3, 2, 3, 4, 5],
        'Valor4': [3, 2, 3, 4, 5],
        'Valor5': [3, 2, 3, 4, 5],
    }
    df = pd.DataFrame(data)

    # Criar um gráfico de radar com Plotly
    fig = px.line_polar(df, r=['Valor1', 'Valor2','Valor3','Valor4','Valor5'], theta='Categoria', line_close=True)

    # Exibir o gráfico no Streamlit
    st.plotly_chart(fig)


# Dicionário com o nome e a função de cada página
paginas = {
    'Página Inicial': pagina_inicio,
    'Autodiagnostico': autodiagnostico,
    'Análise Individual': instituicoes
}

# Barra lateral para selecionar a página
pagina_selecionada = st.sidebar.selectbox('Selecione uma página', list(paginas.keys()))

# Executar a função da página selecionada
paginas[pagina_selecionada]()