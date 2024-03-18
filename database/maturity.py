import pandas as pd
import psycopg2
from sqlalchemy import create_engine
from datetime import datetime

# Configurações do banco de dados PostgreSQL
db_config = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': 'admin',
    'host': 'localhost',
    'port': '5432'
}
conn = None
ind = None
itens = None
nivel = None

# Conectar ao banco de dados PostgreSQL
def get_engine():
    try:
        conn = psycopg2.connect(**db_config)
        print("Conexão realizada com sucesso!")
        #cursor = conn.cursor()

        # Inserir dados na tabela
        return create_engine(f'postgresql+psycopg2://{db_config["user"]}:{db_config["password"]}@{db_config["host"]}:{db_config["port"]}/{db_config["dbname"]}')
        #dados_excel.to_sql('sua_tabela', engine, if_exists='replace', index=False)
    except psycopg2.Error as e:
        print("Erro ao conectar ao banco de dados:", e)

    finally:
        if conn is not None:
            print("Conexão finalizada!")
            conn.close()


def get_itens():
    return pd.read_sql("select * from item", get_engine())

def get_ind():
    return pd.read_sql("SELECT ROW_NUMBER() OVER (ORDER BY e.id, e.descricao, t.titulo, i.descricao) AS linha, "
                       "e.id, "
                       "e.descricao AS Eixo, "
                       "i.descricao as Item, "
                       "t.titulo as Topico "
                       "FROM eixo e "
                       "JOIN item i ON e.id = i.eixo_id "
                       "JOIN topico t ON i.topico_id = t.id "
                       "GROUP BY e.id, e.descricao, t.titulo, i.descricao "
                       "ORDER BY e.id, e.descricao, t.titulo, i.descricao;", get_engine())

def get_eixo():
    return pd.read_sql("SELECT "
                       "e.descricao AS Eixo, "
                       "round(avg(n.valor),2) AS Media "
                       "FROM "
                       "eixo e "
                       "JOIN item i ON e.id = i.eixo_id "
                       "JOIN imgd m ON i.id = m.item_id "
                       "JOIN avaliacao a ON m.id = a.imgd_id "
                       "JOIN nivel n ON n.id = m.nivel_id "
                       "GROUP BY e.descricao;", get_engine())

def get_topico():
    return pd.read_sql("SELECT "
                       "t.titulo AS Topico, "
                       "round(avg(n.valor),2) AS Media "
                       "FROM "
                       "topico t "
                       "JOIN item i ON t.id = i.topico_id "
                       "JOIN imgd m ON i.id = m.item_id "
                       "JOIN avaliacao a ON m.id = a.imgd_id "
                       "JOIN nivel n ON n.id = m.nivel_id "
                       "GROUP BY t.titulo;", get_engine())


def get_nivel():
    return pd.read_sql('select * from nivel', get_engine())

def get_imgd(nivel: int, item: int):
    return pd.read_sql("select i.id from imgd i where i.nivel_id = %s and i.item_id = %s", get_engine(), params=(nivel, item))

def get_gov():
    return pd.read_sql('SELECT i.descricao as Item, ROUND(avg(n.valor), 2) AS Media '
                       ' FROM item i '
                       ' JOIN eixo e ON e.id = i.eixo_id '
                       ' JOIN imgd m ON i.id = m.item_id '
                       ' JOIN avaliacao a ON m.id = a.imgd_id '
                       ' JOIN nivel n ON n.id = m.nivel_id '
                       ' WHERE e.id = 1 '
                       ' GROUP BY i.descricao', get_engine())

def get_gov2():
    return pd.read_sql('SELECT i.descricao as Item, ROUND(avg(n.valor), 2) AS Media '
                       ' FROM item i '
                       ' JOIN eixo e ON e.id = i.eixo_id '
                       ' JOIN imgd m ON i.id = m.item_id '
                       ' JOIN avaliacao a ON m.id = a.imgd_id '
                       ' JOIN nivel n ON n.id = m.nivel_id '
                       ' WHERE e.id = 1 '
                       ' GROUP BY i.descricao '
                       ' HAVING AVG(n.valor) < 2.00', get_engine())

def insert_orgao(df: pd.DataFrame):
    colunas = ['codigoUnidade', 'codigoUnidadePai', 'nome', 'sigla']
    df = df[colunas]
    df.to_sql('instituicao', get_engine(), if_exists='append', index=False)
    print("Dados inseridos com sucesso!")


