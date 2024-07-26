import streamlit as st
from fpdf import FPDF
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

# Function to generate PDF using fpdf2
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'INVOICE', 0, 1, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')

    def chapter_body(self, body):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, body)

def generate_pdf(invoice_data, filename):
    pdf = PDF()
    pdf.add_page()
    pdf.chapter_title(f"Invoice Number: {invoice_data['invoice_number']}")
    pdf.chapter_title(f"Invoice Date: {invoice_data['invoice_date']}")
    pdf.chapter_title(f"Due Date: {invoice_data['due_date']}")
    pdf.chapter_title("Bill To:")
    pdf.chapter_body(f"{invoice_data['client_name']}\n{invoice_data['client_company']}\n{invoice_data['client_address']}\n{invoice_data['client_phone']}\n{invoice_data['client_email']}")

    for item in invoice_data['items']:
        pdf.chapter_body(f"{item['description']} - {item['date']} - {item['hours']}h @ ${item['rate']}/h: ${item['subtotal']}")
    
    pdf.chapter_body(f"Total: ${invoice_data['total']}")
    pdf.chapter_body("Payment Details:")
    pdf.chapter_body(invoice_data['payment_details'])
    
    pdf.output(filename)

# Function to send email
def send_email(receiver_email, subject, body, filename):
    sender_email = "your_email@example.com"
    password = "your_password"
    
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    
    message.attach(MIMEText(body, "plain"))
    
    part = MIMEBase("application", "octet-stream")
    with open(filename, "rb") as attachment:
        part.set_payload(attachment.read())
        
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {os.path.basename(filename)}",
    )
    
    message.attach(part)
    
    server = smtplib.SMTP("smtp.example.com", 587)
    server.starttls()
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message.as_string())
    server.quit()

# Streamlit app
st.title("Invoice Generator")

with st.form("invoice_form"):
    firm_name = st.text_input("Firm Name")
    firm_address = st.text_input("Firm Address")
    firm_phone = st.text_input("Firm Phone")
    firm_email = st.text_input("Firm Email")
    client_name = st.text_input("Client Name")
    client_company = st.text_input("Client Company")
    client_address = st.text_input("Client Address")
    client_phone = st.text_input("Client Phone")
    client_email = st.text_input("Client Email")
    invoice_number = st.text_input("Invoice Number")
    invoice_date = st.date_input("Invoice Date")
    due_date = st.date_input("Due Date")
    payment_details = st.text_area("Payment Details")
    
    items = []
    for i in range(5):
        with st.expander(f"Item {i + 1}"):
            description = st.text_input(f"Description {i + 1}")
            date = st.date_input(f"Date {i + 1}")
            hours = st.number_input(f"Hours {i + 1}", min_value=0.0, step=0.1)
            rate = st.number_input(f"Rate {i + 1}", min_value=0.0, step=0.1)
            subtotal = hours * rate
            items.append({
                "description": description,
                "date": date,
                "hours": hours,
                "rate": rate,
                "subtotal": subtotal,
            })
    
    total = sum(item['subtotal'] for item in items)
    invoice_data = {
        "firm_name": firm_name,
        "firm_address": firm_address,
        "firm_phone": firm_phone,
        "firm_email": firm_email,
        "client_name": client_name,
        "client_company": client_company,
        "client_address": client_address,
        "client_phone": client_phone,
        "client_email": client_email,
        "invoice_number": invoice_number,
        "invoice_date": invoice_date,
        "due_date": due_date,
        "items": items,
        "total": total,
        "payment_details": payment_details,
    }
    
    submit = st.form_submit_button("Generate Invoice")

if submit:
    filename = f"invoice_{invoice_number}.pdf"
    generate_pdf(invoice_data, filename)
    st.success(f"Invoice generated: {filename}")
    
    with open(filename, "rb") as file:
        st.download_button(label="Download Invoice", data=file, file_name=filename, mime="application/pdf")

    email_subject = "Your Invoice"
    email_body = "Please find attached your invoice."
    
    if st.button("Send Email"):
        send_email(client_email, email_subject, email_body, filename)
        st.success(f"Invoice sent to {client_email}")
