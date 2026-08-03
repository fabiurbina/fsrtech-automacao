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
    		
    
    SELECT
            cl.razao_social,
			p.numero_pedido,
			p.etapa,
			e.descricao_etapa,
			p.codigo_cliente,
			data_previsao,
			REGEXP_REPLACE(c.cnpj_cpf, '[^0-9]', '') as cnpj_cpf,
			op.numero_op,
            case  when pro.descricao is null then it.descricao else pro.descricao
            end
            as descricao_produto,
            op.numero_CodProduto,	
            case when op.quantidade is null then it.quantidade else op.quantidade
            end as quantidade,
			op.etapaid,
			case when eop.descricao_etapa is null and rc.dtSugestao is not null then 
			'Requisição de compra' else eop.descricao_etapa end as 'status_producao',
            it.codigo_produto
			
		FROM pedidos p
		LEFT JOIN (SELECT * FROM etapas WHERE descricao_operacao = 'Venda de Produto') e ON e.codigo_etapa = p.etapa
		INNER JOIN clientes c on c.codigo_cliente_omie = p.codigo_cliente
		LEFT JOIN ordem_producao op on op.numero_pedido = p.numero_pedido
		LEFT JOIN requisicoes_compra rc on rc.numero_pedido = p.numero_pedido
		LEFT JOIN (SELECT * FROM etapas WHERE descricao_operacao = 'Ordem de Produção') eop ON eop.codigo_etapa = op.etapaid
        LEFT JOIN produtos pro on pro.codigo_produto = op.numero_CodProduto
        LEFT JOIN clientes cl on cl.codigo_cliente_omie = p.codigo_cliente
        LEFT JOIN itens_pedido it on it.numero_pedido = p.numero_pedido
		WHERE
        (
            eop.descricao_etapa IS NOT NULL
            OR rc.dtSugestao IS NOT NULL
        )
        AND REGEXP_REPLACE(c.cnpj_cpf, '[^0-9]', '') = %s
        group by p.numero_pedido,  it.codigo_produto
        ORDER BY p.data_previsao DESC;
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
    		
    
    SELECT
    
            cl.razao_social,
            p.numero_pedido,
            p.etapa,
            e.descricao_etapa,
            p.codigo_cliente,
            data_previsao,
            REGEXP_REPLACE(c.cnpj_cpf, '[^0-9]', '') as cnpj_cpf,
            op.numero_op,
            case  when pro.descricao is null then it.descricao else pro.descricao
            end
            as descricao_produto,
            op.numero_CodProduto,	
            case when op.quantidade is null then it.quantidade else op.quantidade
            end as quantidade,
            op.etapaid,
            case when eop.descricao_etapa is null and rc.dtSugestao is not null then 
            'Requisição de compra' else eop.descricao_etapa end as 'status_producao',
            it.codigo_produto
			
		FROM pedidos p
		LEFT JOIN (SELECT * FROM etapas WHERE descricao_operacao = 'Venda de Produto') e ON e.codigo_etapa = p.etapa
		INNER JOIN clientes c on c.codigo_cliente_omie = p.codigo_cliente
		LEFT JOIN ordem_producao op on op.numero_pedido = p.numero_pedido
		LEFT JOIN requisicoes_compra rc on rc.numero_pedido = p.numero_pedido
		LEFT JOIN (SELECT * FROM etapas WHERE descricao_operacao = 'Ordem de Produção') eop ON eop.codigo_etapa = op.etapaid
        LEFT JOIN produtos pro on pro.codigo_produto = op.numero_CodProduto
        LEFT JOIN clientes cl on cl.codigo_cliente_omie = p.codigo_cliente
        LEFT JOIN itens_pedido it on it.numero_pedido = p.numero_pedido
		WHERE
        (
            eop.descricao_etapa IS NOT NULL
            OR rc.dtSugestao IS NOT NULL
        )
        group by p.numero_pedido,  it.codigo_produto
        ORDER BY p.data_previsao DESC;
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