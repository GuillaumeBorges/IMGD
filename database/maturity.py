import pandas as pd
import psycopg2
from sqlalchemy import create_engine
from datetime import datetime

# Configurações do banco de dados PostgreSQL
db_config = {
    'dbname': '****',
    'user': '****',
    'password': '****',
    'host': '****',
    'port': '****'
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

def get_itens_eixo():
    return pd.read_sql('SELECT i.descricao as Item, ROUND(avg(n.valor), 2) AS Media, e.descricao AS Eixo '
                       ' FROM item i '
                       ' JOIN eixo e ON e.id = i.eixo_id '
                       ' JOIN imgd m ON i.id = m.item_id '
                       ' JOIN avaliacao a ON m.id = a.imgd_id '
                       ' JOIN nivel n ON n.id = m.nivel_id '
                       ' GROUP BY i.descricao, e.descricao', get_engine())


def get_item():
    return pd.read_sql('SELECT i.descricao as Item, ROUND(avg(n.valor), 2) AS Media '
                       ' FROM item i '
                       ' JOIN eixo e ON e.id = i.eixo_id '
                       ' JOIN imgd m ON i.id = m.item_id '
                       ' JOIN avaliacao a ON m.id = a.imgd_id '
                       ' JOIN nivel n ON n.id = m.nivel_id '
                       ' GROUP BY i.descricao ORDER BY Media desc', get_engine())



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

def get_instituicao():
    return pd.read_sql("select * from instituicao", get_engine())

def get_avaliacao():
    return pd.read_sql("select * from avaliacao", get_engine())

def get_graphic():
    return pd.read_sql("""
                            SELECT
                                ins.sigla as SIGLA,
                                ins.nome AS ORGAO,
                                sum(n.valor) as Ranking,
                                round(avg(n.valor), 2) as Media,
                                a.grupo AS GRUPO
                            FROM
                                instituicao ins
                            JOIN
                                avaliacao a on ins."codigoUnidade" = a.orgao_id
                            JOIN
                                imgd i ON a.imgd_id = i.id
                            JOIN
                                nivel n ON i.nivel_id = n.id
                            GROUP BY
                                ins.sigla, ins.nome, a.grupo
                            """, get_engine())

def get_graphic_pizza():
    return pd.read_sql("""
                        SELECT
                            ROUND(AVG(n.valor), 2) AS Media,
                            a.grupo AS GRUPO,
                            it.descricao AS DESCRICAO_ITEM
                        FROM
                            avaliacao a
                        JOIN
                            imgd i ON a.imgd_id = i.id
                        JOIN
                            nivel n ON i.nivel_id = n.id
                        JOIN
                            item it ON i.item_id = it.id
                        GROUP BY
                            a.grupo, it.descricao
                        ORDER BY
                            a.grupo;
                            """, get_engine())


def get_statistics():
    return pd.read_sql("""
                        SELECT n.valor as Valor,
                               n.descricao AS Nivel,
                               count(Media) AS Instituicoes
                        FROM(SELECT
                            ins.sigla as SIGLA,
                            ins.nome as ORGAO,
                            round(avg(n.valor), 0) as Media
                            FROM instituicao ins
                            JOIN avaliacao a 
                            ON
                                ins."codigoUnidade" = a.orgao_id
                            JOIN imgd i 
                            ON
                                a.imgd_id = i.id
                            JOIN nivel n
                            ON
                                i.nivel_id = n.id
                            GROUP BY ins.sigla, ins.nome

                        ) as instituicoes_por_nivel
                        JOIN nivel n
                        ON
                            instituicoes_por_nivel.Media = n.valor
                        GROUP BY n.valor, n.descricao
                        ORDER BY n.valor; 
                        """, get_engine())

def get_estrategia_dados():
    return pd.read_sql("""
                        SELECT
                            e.descricao AS eixo,
                            i.descricao AS descricao_item,
                            n.descricao AS nivel_maturidade,
                            COUNT(DISTINCT ins."codigoUnidade") AS quantidade_orgaos
                        FROM
                            instituicao ins
                        JOIN
                            avaliacao av ON ins."codigoUnidade" = av.orgao_id
                        JOIN
                            imgd img ON av.imgd_id = img.id
                        JOIN
                            nivel n ON img.nivel_id = n.id
                        JOIN
                            item i ON img.item_id = i.id
                        JOIN
                            eixo e ON i.eixo_id = e.id
                        GROUP BY
                            e.descricao, i.descricao, n.descricao
                        ORDER BY
                            e.descricao, i.descricao, n.descricao;
                        """, get_engine())

def insert_orgao(df: pd.DataFrame):
    colunas = ['codigoUnidade', 'codigoUnidadePai', 'nome', 'sigla']
    df = df[colunas]
    df.to_sql('instituicao', get_engine(), if_exists='append', index=False)
    print("Dados inseridos com sucesso!")


