from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime
from io import BytesIO
import pytz


def gerar_relatorio_pdf(nome_empresa, dados_agendamentos, data_relatorio):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    style_cabecalho = ParagraphStyle(
        name='Cabecalho',
        fontName='Helvetica-Bold',
        fontSize=28,
        textColor=colors.black,
        alignment=1,
        spaceAfter=40,
    )

    style_subcabecalho = ParagraphStyle(
        name='Subcabecalho',
        fontName='Helvetica',
        fontSize=14,
        textColor=colors.black,
        alignment=1,
        spaceAfter=50,
    )

    style_normal = styles['Normal']
    style_normal.fontSize = 10
    style_normal.leading = 12
    style_normal.fontName = 'Helvetica'

    cabecalho_empresa = Paragraph(f"<font size=28><b>{nome_empresa}</b></font>", style_cabecalho)
    fuso_horario = pytz.timezone('America/Sao_Paulo')
    data_atual = datetime.now(fuso_horario).strftime("%d/%m/%Y %H:%M:%S")
    nome_relatorio = Paragraph(f"<font size=16><b>Relação de agendamentos do dia {data_relatorio}</b></font>", style_subcabecalho)
    cabecalho_data = Paragraph(f"<font size=14><i>Relatório gerado em: {data_atual}</i></font>", style_subcabecalho)

    elementos = [cabecalho_empresa, nome_relatorio, cabecalho_data]
    elementos.append(Spacer(1, 40))

    dados_tabela = [['ID Agendamento', 'Data', 'Hora', 'Telefone', 'ID Contato']]

    for agendamento in dados_agendamentos:
        dados_tabela.append([
            agendamento.get('id_agendamento', ''),
            agendamento.get('data', ''),
            agendamento.get('hora', ''),
            agendamento.get('telefone', ''),
            agendamento.get('id_contato', '')
        ])

    tabela_dados = Table(dados_tabela, colWidths=[90, 100, 60, 100, 70])

    estilo_tabela = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.8, 0.8, 0.8)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ])

    tabela_dados.setStyle(estilo_tabela)
    elementos.append(tabela_dados)

    doc.build(elementos)

    buffer.seek(0)
    return buffer



