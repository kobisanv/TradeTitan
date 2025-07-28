import os
import csv
import re
import time
import requests
import smtplib
from bs4 import BeautifulSoup
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

GOOGL_CIK = "1652044"
EDGAR_URL = f"https://data.sec.gov/submissions/CIK000{GOOGL_CIK}.json"

CSV_FILE = "googl_insider_trades.csv"
USER_AGENT = "KobisanVinotharupan kobisan.vinotharupan@gmail.com"
REQUEST_DELAY = 0.005

session = requests.Session()
session.headers.update({"User-Agent": USER_AGENT})

def fetch_form4_filings():
    print("🔍 Fetching EDGAR JSON for AMZN...")
    resp = session.get(EDGAR_URL)
    if resp.status_code != 200:
        print(f"❌ Failed to fetch EDGAR JSON. Status code: {resp.status_code}")
        return []
    data = resp.json()
    recent = data.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    accession_numbers = recent.get("accessionNumber", [])
    primary_docs = recent.get("primaryDocument", [])

    form4_urls = []
    for i, form_type in enumerate(forms):
        if form_type == "4":
            acc_num = accession_numbers[i]
            acc_no_stripped = acc_num.replace("-", "")
            doc = primary_docs[i]
            filing_url = f"https://www.sec.gov/Archives/edgar/data/{GOOGL_CIK}/{acc_no_stripped}/{doc}"
            form4_urls.append(filing_url)
    print(f"✅ Found {len(form4_urls)} Form 4 filings.")
    return form4_urls

def parse_header_info(soup):
    insider_name = "N/A"
    relationship_parts = []

    name_label = soup.find(lambda tag:
        tag.name == "span"
        and "Name and Address of Reporting Person" in tag.get_text()
    )
    if name_label:
        parent_td = name_label.find_parent("td")
        if parent_td:
            a_tag = parent_td.find("a")
            if a_tag:
                insider_name = a_tag.get_text(strip=True)

    rel_label = soup.find(lambda tag:
        tag.name == "span"
        and "Relationship of Reporting Person" in tag.get_text()
    )
    if rel_label:
        parent_td = rel_label.find_parent("td")
        if parent_td:
            rel_table = parent_td.find_next("table")
            if rel_table:
                rows = rel_table.find_all("tr")
                for i, row in enumerate(rows):
                    cells = row.find_all("td")
                    if len(cells) >= 2 and "X" in cells[0].get_text():
                        text = cells[1].get_text(strip=True)
                        if text and text != "Officer (give title below)":
                            relationship_parts.append(text)
                        if "Officer" in text:
                            if i + 1 < len(rows):
                                next_cells = rows[i+1].find_all("td")
                                if len(next_cells) >= 2:
                                    title_text = next_cells[1].get_text(strip=True)
                                    if title_text and title_text != "Officer (give title below)":
                                        relationship_parts.append(title_text)

    relationship_to_issuer = ", ".join(relationship_parts) if relationship_parts else "N/A"
    return insider_name, relationship_to_issuer

def parse_table_i(soup):
    transactions = []
    table_header = soup.find("th", string=lambda s: s and "Table I - Non-Derivative Securities Acquired" in s)
    if not table_header:
        return transactions
    table = table_header.find_parent("table")
    if not table:
        return transactions
    
    tbody = table.find("tbody")
    rows = tbody.find_all("tr") if tbody else table.find_all("tr")
    data_rows = [row for row in rows if not row.find_all("th")]
    
    for row in data_rows:
        cells = row.find_all("td")
        if len(cells) < 9:
            continue
        trade_date = cells[1].get_text(strip=True)
        transaction_code = cells[3].get_text(strip=True)
        transaction_code = re.sub(r"\(\d+\)", "", transaction_code).strip()

        amount_str = cells[5].get_text(strip=True).replace(",", "")
        indicator = cells[6].get_text(strip=True)
        price_str = cells[7].get_text(strip=True)
        price_str = re.sub(r"\(\d+\)", "", price_str)
        price_str = price_str.replace("$", "").replace(",", "").strip()

        owned_str = cells[8].get_text(strip=True).replace(",", "")

        try:
            shares = float(amount_str) if amount_str else 0.0
        except:
            shares = 0.0
        shares_bought = -shares if indicator.upper() == "D" else shares

        try:
            price_per_share = float(price_str) if price_str else 0.0
        except:
            price_per_share = 0.0
        
        try:
            shares_owned = float(owned_str) if owned_str else 0.0
        except:
            shares_owned = 0.0
        
        total_value = abs(shares) * price_per_share
        avg_book_price = total_value / shares_owned if shares_owned > 0 else 0.0

        transactions.append({
            "trade_date": trade_date,
            "transaction_type": transaction_code,
            "shares": shares,
            "shares_bought": shares_bought,
            "price_per_share": price_per_share,
            "shares_owned_after_transaction": shares_owned,
            "total_value": total_value,
            "avg_book_price": avg_book_price
        })
    return transactions

def process_form4(url):
    print(f"Fetching filing: {url}")
    resp = session.get(url)
    if resp.status_code != 200:
        print(f"❌ Failed to fetch: {resp.status_code} for {url}")
        return []
    
    soup = BeautifulSoup(resp.text, "html.parser")
    insider_name, relationship = parse_header_info(soup)
    table_transactions = parse_table_i(soup)
    for tx in table_transactions:
        tx["insider_name"] = insider_name
        tx["relationship_to_issuer"] = relationship
    return table_transactions

def process_all_form4_filings():
    form4_urls = fetch_form4_filings()
    all_transactions = []
    for url in form4_urls:
        txs = process_form4(url)
        all_transactions.extend(txs)
        time.sleep(REQUEST_DELAY)
    return all_transactions

def export_to_csv(transactions, filename=CSV_FILE):
    if not transactions:
        print("⚠️ No transactions found to export.")
        return None
    
    fieldnames = [
        "insider_name",
        "relationship_to_issuer",
        "shares_bought",
        "trade_date",
        "transaction_type",
        "shares",
        "price_per_share",
        "shares_owned_after_transaction",
        "total_value",
        "avg_book_price"
    ]
    with open(filename, mode="w", newline="", encoding="utf-8") as csvf:
        writer = csv.DictWriter(csvf, fieldnames=fieldnames)
        writer.writeheader()
        for tx in transactions:
            writer.writerow({
                "insider_name": tx.get("insider_name", ""),
                "relationship_to_issuer": tx.get("relationship_to_issuer", ""),
                "shares_bought": tx.get("shares_bought", 0),
                "trade_date": tx.get("trade_date", ""),
                "transaction_type": tx.get("transaction_type", ""),
                "shares": tx.get("shares", 0),
                "price_per_share": tx.get("price_per_share", 0),
                "shares_owned_after_transaction": tx.get("shares_owned_after_transaction", 0),
                "total_value": tx.get("total_value", 0),
                "avg_book_price": tx.get("avg_book_price", 0)
            })
    print(f"📊 Exported {len(transactions)} transactions to {filename}")
    return filename

def send_email(csv_path):
    sender = "kobisan.vinotharupan@gmail.com"
    receiver = "kobisan.vinotharupan@gmail.com"
    subject = "GOOGL Insider Trades Report (FORM 4)"
    body = "Attached is the GOOGL insider trades report for ALL Form 4 filings."
    password = os.environ.get("GMAIL_APP_PASSWORD")
    if not password:
        print("❌ GMAIL_APP_PASSWORD environment variable not set!")
        return
    
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = receiver
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    
    with open(csv_path, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(csv_path)}")
    msg.attach(part)
    
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        print(f"📧 Email sent with attachment {csv_path}")
    except Exception as e:
        print("❌ Failed to send email:", e)

def main_task():
    print("Processing all Form 4 filings for GOOGL...")
    transactions = process_all_form4_filings()
    if not transactions:
        print("No transactions found to export.")
        return
    csv_path = export_to_csv(transactions)
    if csv_path:
        send_email(csv_path)

if __name__ == "__main__":
    main_task()
