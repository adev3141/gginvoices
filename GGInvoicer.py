import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

# Function to generate PDF
def generate_pdf(invoice_data, filename):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    c.drawString(30, height - 30, "INVOICE")
    c.drawString(30, height - 60, f"Invoice Number: {invoice_data['invoice_number']}")
    c.drawString(30, height - 90, f"Invoice Date: {invoice_data['invoice_date']}")
    c.drawString(30, height - 120, f"Due Date: {invoice_data['due_date']}")
    
    c.drawString(30, height - 150, "Bill To:")
    c.drawString(30, height - 180, f"{invoice_data['client_name']}")
    c.drawString(30, height - 210, f"{invoice_data['client_company']}")
    c.drawString(30, height - 240, f"{invoice_data['client_address']}")
    c.drawString(30, height - 270, f"{invoice_data['client_phone']}")
    c.drawString(30, height - 300, f"{invoice_data['client_email']}")

    y = height - 330
    for item in invoice_data['items']:
        c.drawString(30, y, f"{item['description']} - {item['date']} - {item['hours']}h @ ${item['rate']}/h: ${item['subtotal']}")
        y -= 30
    
    c.drawString(30, y - 30, f"Total: ${invoice_data['total']}")
    c.drawString(30, y - 60, "Payment Details:")
    c.drawString(30, y - 90, invoice_data['payment_details'])

    c.save()

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
