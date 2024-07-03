from fpdf import FPDF  # pip install fpdf
import json
from datetime import date

class PDF(FPDF):
    def __init__(self, data):
        super().__init__()
        self.data = data["data"]
        self.is_budget = self.data["isbudget"]
        self.lang = self.data["lang"]
        self.add_font('DejaVu', '', 'assets/font/DejaVuSans.ttf', uni=True)
        self.set_font('DejaVu', '', 10)

    def add_header_section(self):
        company = self.data["company"]
        self.set_fill_color(51, 51, 51)
        self.rect(0, 0, self.w, 30, 'F')
        self.set_text_color(252, 255, 255)
        self.set_font('DejaVu', '', 16)
        self.set_xy(10, 10)
        self.cell(0, 10, company["name"], 0, 0, 'L')
        self.set_xy(self.w - 70, 10)
        self.set_font('DejaVu', '', 8)
        self.cell(60, 10, company["contact"], 0, 2, 'R')
        self.ln(20)

    def add_budget_section(self):
        budget_id_prefix = "BU" if self.is_budget else "IN"
        self.data["id"] = budget_id_prefix + self.data["id"]
        
        budget_date = self.data.get("date") or date.today().strftime("%d/%m/%Y")
        
        self.set_text_color(255, 255, 255)
        self.set_font('DejaVu', '', 10)
        table_width = 160
        self.set_x((self.w - table_width) / 2)
        
        for value in [self.data["id"], self.data["customer"], budget_date]:
            self.set_fill_color(51, 51, 51)
            self.cell(50, 10, value, 1, 0, 'C', 1)
            self.set_x(self.get_x() + 5)
        self.ln(10)

    def add_row(self, component, price, widths, table_width):
        if price != 0:
            iva = 0 if self.is_budget else price * 0.21
            total = price + iva
            
            self.set_x((self.w - table_width) / 2)
            self.cell(widths[0], 15, component, 1, 0, 'C')
            self.cell(widths[1], 15, '1', 1, 0, 'C')
            self.cell(widths[2], 15, f"{price:.2f}", 1, 0, 'C')
            self.cell(widths[3], 15, f"{iva:.2f}", 1, 0, 'C')
            self.cell(widths[4], 15, f"{total:.2f}", 1, 0, 'C')
            self.ln()
            return total

    def add_table_section(self):
        self.set_text_color(51, 51, 51)
        self.ln(10)
        self.set_font('DejaVu', '', 10)
        table_width = 160
        self.set_x((self.w - table_width) / 2)
        headers = ['COMPONENT', 'QUANTITY', 'PRICE', 'IVA', 'TOTAL'] if self.lang == "en" else ['COMPONENTE', 'Q', 'PRECIO', 'IVA', 'TOTAL']
        widths = [80, 20, 20, 20, 20]
        
        self.set_text_color(255, 255, 255)
        for header, width in zip(headers, widths):
            self.set_fill_color(51, 51, 51)
            self.cell(width, 10, header, 1, 0, 'C', 1)
        self.ln()
        
        self.set_text_color(51, 51, 51)
        self.set_font('DejaVu', '', 8)
        
        for component, price in self.data["price"].items():
            self.add_row(component, price, widths, table_width)
        
        self.set_font('DejaVu', '', 10)
        self.set_x((self.w - table_width) / 2)
        divider_text = "ANNUAL FEE" if self.lang == "en" else "CUOTA ANUAL"
        self.cell(sum(widths), 10, divider_text, 0, 0, 'L')
        self.ln()
        self.set_font('DejaVu', '', 8)

        for component, price in self.data["annual"].items():
            self.add_row(component, price, widths, table_width)
        
        self.ln(5)

    def add_footer_section(self):
        table_width = 160
        title_width = 50
        value_width = 25

        prices = self.data["price"]
        annuals = self.data["annual"]

        total_price = sum(prices.values())
        total_annual = sum(annuals.values())

        if self.is_budget:
            titles = ['TOTAL', 'ANNUAL FEE', 'TOTAL + ANNUAL FEE'] if self.lang == "en" else ['TOTAL', 'CUOTA ANUAL', 'SUMATORIO']
            values = [total_price, total_annual, total_price + total_annual]
        else:
            total_price_iva = total_price * 1.21
            total_annual_iva = total_annual * 1.21
            titles = ['TOTAL', 'ANNUAL FEE', 'TOTAL + IVA', 'ANNUAL FEE + IVA', '(TOTAL + ANNUAL FEE) + IVA'] if self.lang == "en" else ['TOTAL', 'CUOTA ANUAL', 'TOTAL CON IVA', 'CUOTA ANUAL CON IVA', 'SUMATORIO CON IVA']
            values = [total_price, total_annual, total_price_iva, total_annual_iva, total_price_iva + total_annual_iva]

        self.ln(5)
        for title, value in zip(titles, values):
            self.set_x((self.w - table_width) / 2)
            self.set_text_color(255, 255, 255)
            self.set_font('DejaVu', '', 10)
            self.cell(title_width, 10, title, 1, 0, 'C', 1)
            self.set_text_color(51, 51, 51)
            self.set_font('DejaVu', '', 10)
            self.cell(value_width, 10, f"{value:.2f} €", 1, 1, 'C')

    def create_pdf(self):
        dir = "output/budgets/" if self.is_budget else "output/invoices/"
        
        self.add_page()
        self.add_header_section()
        self.add_budget_section()
        self.add_table_section()
        self.add_footer_section()
        file_dir = f"{dir}{self.data['id']}.pdf"
        self.output(file_dir)
        print(file_dir)

def get_data(doc):
    with open(doc, 'r', encoding='utf-8') as f:
        return json.load(f)

JSON_DIR = "data.json"
budget_obj = get_data(JSON_DIR)
pdf = PDF(budget_obj)
pdf.create_pdf()