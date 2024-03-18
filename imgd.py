import pandas as pd
import plotly.express as px
import streamlit as st
from database.maturity import get_ind, get_eixo, get_topico, get_gov, get_gov2
import networkx as nx
import plotly.graph_objects as go

st.set_page_config(layout='wide', page_icon='icon.jpeg', page_title='Maturidade de Governança de Dados')
df = pd.read_excel('autodiagnostico.xlsx')
# Buscando dados dos Itens
itens = get_ind()
eixo = get_eixo()
topico = get_topico()
gov = get_gov()
gov2 = get_gov2()

def pagina_inicio():
    st.title('Infraestrutura Nacional de Dados')
    st.write(
        'Este projeto visa avaliar e acompanhar o nível de maturidade da governança de dados em diferentes organizações.')
    st.subheader('Métricas da Estrutura:')

    eixo = st.sidebar.selectbox("Eixo", itens['eixo'].unique())
    df_filtered = itens[itens['eixo'] == eixo]

    cola, colb, colc, cold = st.columns(4)
    col3, col4 = st.columns(2)
    col5, col6 = st.columns(2)

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

    with col5:

        # Criar um novo grafo direcionado
        G = nx.DiGraph()

        # Adicionar nós ao grafo
        G.add_node(eixo)
        G.add_nodes_from(df_filtered['item'])

        for item in df_filtered['item']:
            # Adicionar arestas ao grafo
            G.add_edge(eixo, item)

        # Converter o gráfico do NetworkX para um gráfico do Plotly
        pos = nx.spring_layout(G)  # Calcular a posição dos nós
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.append(x0)
            edge_x.append(x1)
            edge_x.append(None)
            edge_y.append(y0)
            edge_y.append(y1)
            edge_y.append(None)

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines')

        node_x = []
        node_y = []
        node_text = []
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(node)

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            text=node_text,
            textposition="top center",
            hoverinfo='text',
            marker=dict(
                showscale=True,
                colorscale='YlGnBu',
                reversescale=True,
                color=[],
                size=10,
                colorbar=dict(
                    thickness=15,
                    title='Mapa Mental',
                    xanchor='left',
                    titleside='right'
                ),
                line_width=2))

        node_trace.marker.color = [len(G.adj[node]) for node in G.nodes()]
        node_trace.text = node_text

        # Criar o layout do gráfico
        fig = go.Figure(data=[edge_trace, node_trace],
                        layout=go.Layout(
                            title=f'Mapa Mental - Eixo: {eixo}',
                            titlefont_size=16,
                            showlegend=False,
                            hovermode='closest',
                            margin=dict(b=20, l=5, r=5, t=40),
                            annotations=[dict(
                                text="",
                                showarrow=False,
                                xref="paper", yref="paper",
                                x=0.005, y=-0.002)],
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))

        # Exibir o gráfico no Streamlit

        st.plotly_chart(fig, height=600, width=2000)

    with col6:

        st.markdown(f"### Itens de Maturidade - Eixo: {eixo}")
        st.write("Aqui está uma breve descrição do DataFrame.")
        df_filtered.index = df_filtered.index + 1
        st.dataframe(df_filtered, column_order=['item','eixo','topico'])

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
    colb.metric('Órgãos', df['orgao'].nunique())
    colc.metric('Média Geral', df['NIVEL'].mean().round(0))
    cold.metric('Itens', itens['item'].count())

    # Gráfico Barra Geral
    fig_data_total = px.bar(df, x='SIGLA', y='NIVEL', color='Ranking', title='Maturidade de Dados - Geral', text='orgao')
    col1.plotly_chart(fig_data_total, use_container_width=True)

    # Gráfico Barra por Grupo
    fig_data_por_grupo = px.bar(df_filtered, x='SIGLA', y='NIVEL', color='Ranking', title=f'Maturidade de Dados - {grupo.title()}', text='orgao')
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

    st.markdown(f"### Dados do Grupo - {grupo}")
    st.write("Aqui está uma breve descrição:")
    st.dataframe(df_filtered)

def egd():
    st.title('EGD -> Estratégia de Dados')
    st.write('Este projeto visa avaliar e acompanhar as informações do autodiagnóstico para melhorar a governança de dados em diferentes organizações.')
    st.subheader('Métricas da Estratégia:')

    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    df_eixo = eixo
    fig_pie = px.pie(df_eixo, values='media', names='eixo', title='Eixos da Infraestrutura Nacional de Dados', hole=0.5)
    fig_pie.update_traces(textinfo='percent + value')
    col1.plotly_chart(fig_pie, use_container_width=True)

    df_topico = topico
    fig_pie2 = px.pie(df_topico, values='media', names='topico', title='Tópicos da Maturidade de Dados', hole=0.5)
    fig_pie2.update_traces(textinfo='percent + value')
    col2.plotly_chart(fig_pie2, use_container_width=True)

    df_gov = gov
    fig_pie3 = px.pie(df_gov, values='media', names='item', title='Itens do Eixo de Governança de Dados', hole=0.5, height=500, width=800)
    fig_pie3.update_traces(textinfo='percent + value')
    col3.plotly_chart(fig_pie3, use_container_width=True)

    df_gov2 = gov2
    fig_pie4 = px.pie(df_gov2, values='media', names='item', title='Itens do Eixo de Governança de Dados (< 2,00)', hole=0.5, height=500, width=800)
    fig_pie4.update_traces(textinfo='percent + value')
    col4.plotly_chart(fig_pie4, use_container_width=True)

    #col[eixo] = st.columns(len(df_eixo))
    #col1, col2 = st.columns(2)
    #col3, col4 = st.columns(2)




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
    'Infraestrutura': pagina_inicio,
    'Autodiagnostico': autodiagnostico,
    'Estratégia de Dados': egd,
    'Análise Individual': instituicoes
}

# Barra lateral para selecionar a página
pagina_selecionada = st.sidebar.selectbox('Selecione uma página', list(paginas.keys()))

# Executar a função da página selecionada
paginas[pagina_selecionada]()
