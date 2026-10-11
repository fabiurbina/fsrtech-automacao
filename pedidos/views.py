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
    recebe os dados do formulário e gera uma proposta comercial em PDF.
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

    # Aceita valores no padrão brasileiro (1.500,00) e também decimal (1500.00).
    valor_bruto = request.POST.get("valor", "").strip().replace("R$", "").replace(" ", "")
    try:
        if "," in valor_bruto:
            valor_bruto = valor_bruto.replace(".", "").replace(",", ".")
        valor = Decimal(valor_bruto)
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

    from datetime import date
    from io import BytesIO
    from xml.sax.saxutils import escape

    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether

    buffer = BytesIO()
    navy = colors.HexColor("#102A43")
    blue = colors.HexColor("#2563EB")
    pale = colors.HexColor("#EFF6FF")
    light = colors.HexColor("#F4F7FB")
    ink = colors.HexColor("#243447")
    muted = colors.HexColor("#61758A")
    border = colors.HexColor("#D9E2EC")
    white = colors.white

    documento = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=13 * mm,
        bottomMargin=23 * mm,
        title=f"Proposta comercial - {dados['titulo']}",
        author=dados["empresa"],
    )

    estilos = getSampleStyleSheet()
    estilos.add(ParagraphStyle(
        name="FSRBrand", fontName="Helvetica-Bold", fontSize=22, leading=25,
        textColor=white, spaceAfter=2,
    ))
    estilos.add(ParagraphStyle(
        name="FSRBrandSub", fontName="Helvetica", fontSize=7.5, leading=10,
        textColor=colors.HexColor("#D7E6F7"),
    ))
    estilos.add(ParagraphStyle(
        name="FSRDocTitle", fontName="Helvetica-Bold", fontSize=16, leading=19,
        textColor=navy, spaceAfter=3,
    ))
    estilos.add(ParagraphStyle(
        name="FSRSub", fontName="Helvetica", fontSize=8.5, leading=11,
        textColor=muted,
    ))
    estilos.add(ParagraphStyle(
        name="FSRSection", fontName="Helvetica-Bold", fontSize=9.5, leading=12,
        textColor=navy, spaceBefore=1, spaceAfter=5,
    ))
    estilos.add(ParagraphStyle(
        name="FSRLabel", fontName="Helvetica-Bold", fontSize=7, leading=9,
        textColor=muted,
    ))
    estilos.add(ParagraphStyle(
        name="FSRValue", fontName="Helvetica", fontSize=8.5, leading=11,
        textColor=ink,
    ))
    estilos.add(ParagraphStyle(
        name="FSRValueBold", fontName="Helvetica-Bold", fontSize=8.5, leading=11,
        textColor=navy,
    ))
    estilos.add(ParagraphStyle(
        name="FSRScope", fontName="Helvetica", fontSize=8.5, leading=12,
        textColor=ink,
    ))
    estilos.add(ParagraphStyle(
        name="FSRAmtLabel", fontName="Helvetica-Bold", fontSize=7.5, leading=9,
        textColor=colors.HexColor("#D7E6F7"),
    ))
    estilos.add(ParagraphStyle(
        name="FSRAmt", fontName="Helvetica-Bold", fontSize=20, leading=23,
        textColor=white,
    ))
    estilos.add(ParagraphStyle(
        name="FSRSmall", fontName="Helvetica", fontSize=7, leading=9,
        textColor=muted,
    ))

    def texto(valor_texto):
        # Escape conteúdo digitado pelo usuário e preservar quebras de linha.
        return escape(str(valor_texto or "")).replace("\n", "<br/>")

    def p(valor_texto, estilo="FSRValue"):
        return Paragraph(texto(valor_texto), estilos[estilo])

    def rodape(canvas, doc):
        canvas.saveState()
        largura, altura = A4
        canvas.setFillColor(blue)
        canvas.rect(0, altura - 3 * mm, largura, 3 * mm, stroke=0, fill=1)
        canvas.setStrokeColor(border)
        canvas.setLineWidth(0.6)
        canvas.line(18 * mm, 16 * mm, largura - 18 * mm, 16 * mm)
        canvas.setFont("Helvetica-Bold", 7)
        canvas.setFillColor(navy)
        canvas.drawString(18 * mm, 10 * mm, dados["empresa"][:60])
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(muted)
        canvas.drawRightString(largura - 18 * mm, 10 * mm, f"PROPOSTA COMERCIAL  •  Página {doc.page}")
        canvas.restoreState()

    story = []

    contato_empresa = " • ".join(
        escape(item) for item in [dados["email_empresa"], dados["telefone_empresa"]] if item
    )
    emissao = date.today().strftime("%d/%m/%Y")
    validade = dados["validade"] or "15 dias"

    cabecalho = Table([[
        [Paragraph(texto(dados["empresa"]), estilos["FSRBrand"]),
         Paragraph("AUTOMAÇÃO • INTEGRAÇÕES • FERRAMENTAS DIGITAIS", estilos["FSRBrandSub"])],
        [Paragraph("PROPOSTA COMERCIAL", estilos["FSRBrandSub"]),
         Paragraph("<b>ORÇAMENTO</b>", estilos["FSRBrandSub"]),
         Spacer(1, 2 * mm),
         Paragraph(f"Emissão: {emissao}", estilos["FSRBrandSub"]),
         Paragraph(f"Validade: {texto(validade)}", estilos["FSRBrandSub"])]
    ]], colWidths=[112 * mm, 62 * mm])
    cabecalho.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), navy),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 4 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4 * mm),
    ]))
    story += [cabecalho, Spacer(1, 5 * mm),
              p("Proposta de serviço", "FSRDocTitle"),
              p("Documento comercial com escopo, investimento e condições iniciais do serviço.", "FSRSub"),
              Spacer(1, 4 * mm)]

    dados_empresa = [
        p("DADOS DA EMPRESA", "FSRLabel"), Spacer(1, 1 * mm),
        p("Contato", "FSRValueBold"),
        p(dados["email_empresa"] or "E-mail não informado"),
        p(dados["telefone_empresa"] or "Telefone não informado"),
    ]
    dados_cliente = [
        p("DADOS DO CLIENTE", "FSRLabel"), Spacer(1, 1 * mm),
        p("Cliente", "FSRValueBold"), p(dados["cliente"]),
        p("E-mail", "FSRValueBold"), p(dados["email_cliente"] or "Não informado"),
    ]
    cartoes = Table([[dados_empresa, dados_cliente]], colWidths=[87 * mm, 87 * mm])
    cartoes.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), light),
        ("BACKGROUND", (1, 0), (1, 0), pale),
        ("BOX", (0, 0), (0, 0), 0.6, border),
        ("BOX", (1, 0), (1, 0), 0.6, border),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 3 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3 * mm),
    ]))
    story += [cartoes, Spacer(1, 4 * mm), p("01  Serviço contratado", "FSRSection")]

    servico = Table([
        [p("SERVIÇO", "FSRLabel"), p("PRAZO ESTIMADO", "FSRLabel")],
        [p(dados["titulo"], "FSRValueBold"), p(dados["prazo"] or "A combinar", "FSRValueBold")],
    ], colWidths=[126 * mm, 48 * mm])
    servico.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), light),
        ("BOX", (0, 0), (-1, -1), 0.6, border),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, border),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 2 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2 * mm),
    ]))
    story += [servico, Spacer(1, 4 * mm), p("02  Descrição e escopo", "FSRSection")]

    escopo = Table([[p(dados["descricao"], "FSRScope")]], colWidths=[174 * mm])
    escopo.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.7, border),
        ("LINEBEFORE", (0, 0), (0, 0), 3, blue),
        ("LEFTPADDING", (0, 0), (-1, -1), 4 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 3 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3 * mm),
    ]))
    story += [escopo, Spacer(1, 4 * mm), p("03  Investimento e condições", "FSRSection")]

    valor_formatado = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    condicoes_linhas = [
        [p("VALIDADE DA PROPOSTA", "FSRLabel"), p(validade, "FSRValueBold")],
        [p("PRAZO ESTIMADO", "FSRLabel"), p(dados["prazo"] or "A combinar", "FSRValueBold")],
    ]
    if dados["condicoes"]:
        condicoes_linhas.append([p("CONDIÇÕES COMERCIAIS", "FSRLabel"), p(dados["condicoes"], "FSRValue")])

    tabela_condicoes = Table(condicoes_linhas, colWidths=[48 * mm, 25 * mm])
    tabela_condicoes.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, border),
        ("LEFTPADDING", (0, 0), (-1, -1), 2 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 1 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 2 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2 * mm),
    ]))
    investimento = Table([[
        [p("INVESTIMENTO TOTAL", "FSRAmtLabel"), Spacer(1, 1 * mm), p(valor_formatado, "FSRAmt")],
        tabela_condicoes
    ]], colWidths=[88 * mm, 86 * mm])
    investimento.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), blue),
        ("BACKGROUND", (1, 0), (1, 0), light),
        ("BOX", (0, 0), (-1, -1), 0.6, border),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 3 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3 * mm),
    ]))
    story += [investimento, Spacer(1, 4 * mm), p("04  Próximos passos", "FSRSection")]

    passos = Table([
        [p("1. Aprovação", "FSRValueBold"), p("Confirmação do escopo e das condições comerciais.")],
        [p("2. Formalização", "FSRValueBold"), p("Alinhamento das condições finais e contrato, quando aplicável.")],
        [p("3. Início", "FSRValueBold"), p("Agendamento após aprovação entre as partes.")],
    ], colWidths=[35 * mm, 139 * mm])
    passos.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, border),
        ("LEFTPADDING", (0, 0), (-1, -1), 1 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 1.5 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5 * mm),
    ]))
    story += [passos, Spacer(1, 3 * mm)]

    observacao = (
        "<b>Observação</b> — Este documento é uma proposta comercial. O início do serviço depende "
        "da aprovação entre as partes. Condições de pagamento e entregáveis detalhados devem ser "
        "confirmados antes da contratação."
    )
    aviso = Table([[Paragraph(observacao, estilos["FSRSmall"])]], colWidths=[174 * mm])
    aviso.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("BOX", (0, 0), (-1, -1), 0.5, border),
        ("LEFTPADDING", (0, 0), (-1, -1), 3 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 2 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2 * mm),
    ]))
    story += [aviso, Spacer(1, 2 * mm),
              p("Ferramentas digitais • Automação • Desenvolvimento de sistemas", "FSRSmall")]

    documento.build(story, onFirstPage=rodape, onLaterPages=rodape)
    pdf = buffer.getvalue()
    buffer.close()

    resposta = HttpResponse(pdf, content_type="application/pdf")
    resposta["Content-Disposition"] = 'attachment; filename="orcamento-fsrtech.pdf"'
    return resposta
