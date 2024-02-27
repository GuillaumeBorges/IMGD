import pandas as pd
import psycopg2
from sqlalchemy import create_engine

# Configurações do banco de dados PostgreSQL
db_config = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': '*****',
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


def get_nivel():
    return pd.read_sql("", get_engine())
