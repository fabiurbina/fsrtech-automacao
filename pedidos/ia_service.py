def gerar_resumo(indicadores):
    """
    Gera um resumo inteligente da produção.

    Esta primeira versão utiliza regras simples.
    Posteriormente será substituída por um modelo de IA.
    """

    pedido = indicadores["numero_pedido"]
    op = indicadores["codigo_op"]

    tempo = indicadores["tempo_total_min"]
    etapas = indicadores["total_etapas"]
    tempo_medio = indicadores["tempo_medio_etapa_min"]

    peso = indicadores["peso_real_fracionamento_kg"]
    quantidade = indicadores["quantidade_prevista_envase_un"]

    perdas = indicadores["perda_fracionamento_kg"]

    texto = f"""
A Ordem de Produção {op}, vinculada ao Pedido {pedido},
foi concluída após passar por {etapas} etapas produtivas.

Durante o processo foram produzidos aproximadamente
{peso:,.3f} kg, correspondentes a
{quantidade:,.0f} unidades.

O tempo total registrado foi de
{tempo} minutos,
com média de {tempo_medio:.1f} minutos por etapa.
"""

    if perdas == 0:

        texto += """

Não foram registradas perdas produtivas durante a fabricação,
indicando excelente aproveitamento dos insumos e estabilidade
durante o processo.

"""

    else:

        texto += f"""

Foram registradas perdas de aproximadamente
{perdas:.3f} kg durante o processo produtivo.
Recomenda-se avaliar as etapas com maior impacto para identificar
oportunidades de melhoria.

"""

    texto += """

Os indicadores demonstram o desempenho geral desta Ordem de Produção.
Nas próximas versões, o Viesano Insights utilizará Inteligência Artificial
para comparar este resultado com o histórico da fábrica e identificar
automaticamente gargalos, desvios e oportunidades de otimização.

"""

    return texto.strip()