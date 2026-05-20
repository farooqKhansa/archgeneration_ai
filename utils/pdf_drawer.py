from fpdf import FPDF
from utils.pdf_drawer import draw_microservice_diagram

def draw_box(pdf, x, y, w, h, text):
    pdf.rect(x, y, w, h)
    pdf.set_xy(x, y + h / 3)
    pdf.set_font("Helvetica", size=10)
    pdf.multi_cell(w, 5, text, align="C")


def draw_arrow(pdf, x1, y1, x2, y2):
    pdf.line(x1, y1, x2, y2)

    # arrow head
    pdf.line(x2, y2, x2 - 2, y2 - 2)
    pdf.line(x2, y2, x2 - 2, y2 + 2)


def draw_microservice_diagram(pdf):
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Microservices Architecture", ln=True)

    # API Gateway
    draw_box(pdf, 80, 40, 50, 15, "API Gateway")

    # Services
    draw_box(pdf, 20, 80, 40, 15, "Auth Service")
    draw_box(pdf, 80, 80, 40, 15, "Chat Service")
    draw_box(pdf, 140, 80, 40, 15, "Notification Service")

    # Database
    draw_box(pdf, 80, 130, 50, 15, "PostgreSQL")

    # Arrows
    draw_arrow(pdf, 105, 55, 40, 80)
    draw_arrow(pdf, 105, 55, 100, 80)
    draw_arrow(pdf, 105, 55, 160, 80)

    draw_arrow(pdf, 40, 95, 105, 130)
    draw_arrow(pdf, 100, 95, 105, 130)
    draw_arrow(pdf, 160, 95, 105, 130)