# mysql_service.py

import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

def consultar_pedidos_cliente(cpf_cnpj):

    conn = pymysql.connect(
        host=os.getenv("HOST"),
        user=os.getenv("USER"),
        password=os.getenv("PASSWORD"),
        database=os.getenv("DATABASE"),
        charset="utf8mb4"
    )

    cursor = conn.cursor(pymysql.cursors.DictCursor)

    sql = """
    		
    SELECT * FROM ViesanoDW.PipelineCli 
    WHERE REGEXP_REPLACE(cnpj_cpf, '[^0-9]', '') = %s; 
    
    """

    cursor.execute(sql, (cpf_cnpj,))

    resultado = cursor.fetchall()

    cursor.close()
    conn.close()
    print("Filtro recebido:", cpf_cnpj)
    return resultado
    
    
def consultar_todos_pedidos():
    conn = pymysql.connect(
        host=os.getenv("HOST"),
        user=os.getenv("USER"),
        password=os.getenv("PASSWORD"),
        database=os.getenv("DATABASE"),
        charset="utf8mb4"
    )

    cursor = conn.cursor(pymysql.cursors.DictCursor)

    sql = """
    		
    
    SELECT * FROM ViesanoDW.PipelineCli;
    
    """

    cursor.execute(sql)

    resultado = cursor.fetchall()

    cursor.close()
    conn.close()
    return resultado


def consultar_indicadores_producao(numero_codop):

    conn = pymysql.connect(
        host=os.getenv("HOST"),
        user=os.getenv("USER"),
        password=os.getenv("PASSWORD"),
        database=os.getenv("DATABASE"),
        charset="utf8mb4"
    )

    cursor = conn.cursor(pymysql.cursors.DictCursor)

    sql = """
        SELECT *
        FROM vw_resumo_producao
        WHERE numero_CodOP = %s
    """

    cursor.execute(sql, (numero_codop,))

    resultado = cursor.fetchone()

    cursor.close()
    conn.close()

    return resultado