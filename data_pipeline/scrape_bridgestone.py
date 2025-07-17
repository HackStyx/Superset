import requests
from bs4 import BeautifulSoup, Tag
import pdfplumber
import re
import os
from sqlalchemy import create_engine
from config import BRIDGESTONE_IR_URL, POSTGRES_URI
import tempfile
import pandas as pd
from difflib import get_close_matches

def get_pdf_links():
    r = requests.get(BRIDGESTONE_IR_URL)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")
    links = []
    for a in soup.find_all("a", href=True):
        if not isinstance(a, Tag):
            continue
        href = a.get('href', '')
        text = a.get_text()
        if (
            isinstance(href, str) and href.endswith(".pdf") and
            ("2023" in text or "2024" in text or "2025" in text) and
            ("Consolidated Financial Statements" in text or "Consolidated Financial statements" in text)
        ):
            links.append((text, href if href.startswith("http") else f"https://www.bridgestone.com{href}"))
    return links

def fuzzy_find(row, targets):
    for cell in row:
        match = get_close_matches(cell.lower(), targets, n=1, cutoff=0.7)
        if match:
            return match[0], cell
    return None, None

def extract_year_quarter(text, pdf_path):
    year_match = re.search(r"(2023|2024|2025)", text)
    quarter_match = re.search(r"Q([1-4])", text, re.IGNORECASE)
    year = int(year_match.group(1)) if year_match else None
    quarter = f"Q{quarter_match.group(1)}" if quarter_match else None
    if not year or not quarter:
        with pdfplumber.open(pdf_path) as pdf:
            first_page = pdf.pages[0]
            page_text = first_page.extract_text() or ""
            if not year:
                year_match = re.search(r"(2023|2024|2025)", page_text)
                year = int(year_match.group(1)) if year_match else None
            if not quarter:
                quarter_match = re.search(r"Q([1-4])", page_text, re.IGNORECASE)
                quarter = f"Q{quarter_match.group(1)}" if quarter_match else None
    if not year:
        year = None
    if not quarter:
        quarter = "Unknown"
    return year, quarter

def extract_financials_from_pdf(pdf_path, link_text):
    found = {}
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                df = pd.DataFrame(table)
                for idx, row in df.iterrows():
                    row_strs = [str(x).strip() for x in row if x]
                    for target in ["revenue", "gross profit"]:
                        match, cell = fuzzy_find(row_strs, [target])
                        if match:
                            for val in row_strs:
                                if re.match(r"^[\d,]+$", val):
                                    found[match] = int(val.replace(",", ""))
            text = page.extract_text() or ""
            for target in ["revenue", "gross profit"]:
                regex = re.compile(target + r"[\s:]+([\d,]+)", re.IGNORECASE)
                m = regex.search(text)
                if m:
                    found[target] = int(m.group(1).replace(",", ""))
    if found.get("revenue") and found.get("gross profit"):
        year, quarter = extract_year_quarter(link_text, pdf_path)
        return {"year": year, "quarter": quarter, "revenue": found["revenue"], "gross_profit": found["gross profit"]}
    return None

def main():
    engine = create_engine(POSTGRES_URI)
    links = get_pdf_links()
    print(f"Found {len(links)} PDF links.")
    for text, url in links:
        print(f"Downloading {url}")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            r = requests.get(url)
            tmp.write(r.content)
            tmp.flush()
            data = extract_financials_from_pdf(tmp.name, text)
            if data:
                with engine.begin() as conn:
                    conn.execute(
                        """
                        INSERT INTO bridgestone_financials (year, quarter, revenue, gross_profit)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (year, quarter) DO NOTHING
                        """,
                        (data["year"], data["quarter"], data["revenue"], data["gross_profit"])
                    )
                print(f"Inserted: {data}")
            else:
                print(f"Could not extract data from {url}")
        os.unlink(tmp.name)

if __name__ == "__main__":
    main() 