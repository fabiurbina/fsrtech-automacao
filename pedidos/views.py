from io import BytesIO
from decimal import Decimal, InvalidOperation

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


def home(request):
    return render(request, 'home.html')


def criacao_de_sites(request):
    return render(request, 'criacao_de_sites.html')


@require_http_methods(["GET", "POST"])
def orcamento_facil(request):
    """
    MVP sem IA e sem banco de dados:
    recebe os dados do formulário e gera um PDF para download.
    """
    if request.method == "GET":
        return render(request, "orcamento_facil.html")

    dados = {
        "empresa": request.POST.get("empresa", "").strip()[:120],
        "email_empresa": request.POST.get("email_empresa", "").strip()[:160],
        "telefone_empresa": request.POST.get("telefone_empresa", "").strip()[:50],
        "cliente": request.POST.get("cliente", "").strip()[:160],
        "email_cliente": request.POST.get("email_cliente", "").strip()[:160],
        "titulo": request.POST.get("titulo", "").strip()[:160],
        "descricao": request.POST.get("descricao", "").strip()[:5000],
        "prazo": request.POST.get("prazo", "").strip()[:120],
        "validade": request.POST.get("validade", "15 dias").strip()[:40],
        "condicoes": request.POST.get("condicoes", "").strip()[:2000],
    }

    try:
        valor = Decimal(request.POST.get("valor", "").replace(".", "").replace(",", "."))
        if not valor.is_finite() or valor < 0:
            raise InvalidOperation
    except (InvalidOperation, ValueError):
        return render(
            request,
            "orcamento_facil.html",
            {"dados": dados, "erro": "Informe um valor válido para o orçamento."},
            status=400,
        )

    campos_obrigatorios = ("empresa", "cliente", "titulo", "descricao")
    if any(not dados[campo] for campo in campos_obrigatorios):
        return render(
            request,
            "orcamento_facil.html",
            {"dados": dados, "erro": "Preencha empresa, cliente, título e descrição do serviço."},
            status=400,
        )

    buffer = BytesIO()
    documento = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2.0 * cm,
        leftMargin=2.0 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.8 * cm,
        title=f"Orçamento - {dados['titulo']}",
        author=dados["empresa"],
    )

    estilos = getSampleStyleSheet()
    estilos.add(ParagraphStyle(
        name="MarcaFSR", parent=estilos["Title"], fontName="Helvetica-Bold",
        fontSize=21, leading=25, textColor=colors.HexColor("#1d4ed8"),
        alignment=TA_LEFT, spaceAfter=4,
    ))
    estilos.add(ParagraphStyle(
        name="SubtituloAzul", parent=estilos["Heading2"], fontName="Helvetica-Bold",
        fontSize=13, leading=17, textColor=colors.HexColor("#0f172a"),
        spaceBefore=12, spaceAfter=7,
    ))
    estilos.add(ParagraphStyle(
        name="CorpoSeguro", parent=estilos["BodyText"], fontName="Helvetica",
        fontSize=9.5, leading=14, textColor=colors.HexColor("#334155"),
        spaceAfter=5,
    ))
    estilos.add(ParagraphStyle(
        name="Pequeno", parent=estilos["BodyText"], fontName="Helvetica",
        fontSize=8, leading=11, textColor=colors.HexColor("#64748b"),
    ))

    def p(texto, estilo="CorpoSeguro"):
        # Escapa caracteres que poderiam ser interpretados como marcação pelo Paragraph.
        from xml.sax.saxutils import escape
        texto = escape(str(texto or "")).replace("\n", "<br/>")
        return Paragraph(texto, estilos[estilo])

    story = [
        p(dados["empresa"], "MarcaFSR"),
        p("PROPOSTA COMERCIAL / ORÇAMENTO", "SubtituloAzul"),
        Spacer(1, 0.25 * cm),
    ]

    contato_empresa = " • ".join(x for x in [dados["email_empresa"], dados["telefone_empresa"]] if x)
    if contato_empresa:
        story += [p(contato_empresa, "Pequeno"), Spacer(1, 0.25 * cm)]

    info = [
        [p("<b>Cliente</b>"), p(dados["cliente"])],
        [p("<b>E-mail do cliente</b>"), p(dados["email_cliente"] or "Não informado")],
        [p("<b>Serviço</b>"), p(dados["titulo"])],
    ]
    tabela = Table(info, colWidths=[4.0 * cm, 12.0 * cm], hAlign="LEFT")
    tabela.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eff6ff")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#dbeafe")),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#dbeafe")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story += [tabela, p("Descrição e escopo do serviço", "SubtituloAzul"), p(dados["descricao"])]

    valor_formatado = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    resumo = [
        [p("<b>Investimento</b>"), p(f"<b>{valor_formatado}</b>")],
        [p("<b>Prazo estimado</b>"), p(dados["prazo"] or "A combinar")],
        [p("<b>Validade da proposta</b>"), p(dados["validade"] or "15 dias")],
    ]
    tabela_resumo = Table(resumo, colWidths=[5.0 * cm, 11.0 * cm], hAlign="LEFT")
    tabela_resumo.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eff6ff")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#dbeafe")),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#dbeafe")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story += [Spacer(1, 0.35 * cm), tabela_resumo]

    if dados["condicoes"]:
        story += [p("Condições comerciais", "SubtituloAzul"), p(dados["condicoes"])]

    story += [
        Spacer(1, 0.8 * cm),
        p("Este documento é uma proposta comercial. O início do serviço depende da aprovação entre as partes.", "Pequeno"),
    ]

    def rodape(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#dbeafe"))
        canvas.line(2 * cm, 1.45 * cm, A4[0] - 2 * cm, 1.45 * cm)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#64748b"))
        canvas.drawString(2 * cm, 1.05 * cm, dados["empresa"])
        canvas.drawRightString(A4[0] - 2 * cm, 1.05 * cm, f"Página {doc.page}")
        canvas.restoreState()

    documento.build(story, onFirstPage=rodape, onLaterPages=rodape)
    pdf = buffer.getvalue()
    buffer.close()

    nome_arquivo = "orcamento-fsrtech.pdf"
    resposta = HttpResponse(pdf, content_type="application/pdf")
    resposta["Content-Disposition"] = f'attachment; filename="{nome_arquivo}"'
    return resposta
