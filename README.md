# Alibaba_Webscraper

A Python Selenium-based scraper for collecting RFQ (Request for Quotation) listings from Alibaba's sourcing site. This tool automates the extraction of detailed buyer requirements across multiple pages and saves the data in CSV format for easy analysis.

---

## How It Works

1. Opens Alibaba's RFQ search listing with pagination support (up to 100 pages).
2. On each page, automatically collects all RFQ cards.
3. Opens each RFQ detail page in a background tab to extract the RFQ ID.
4. Extracts fields such as title, buyer name, quantity (with units), country, quotes left, buyer badges (like Email Confirmed), inquiry URL, and inquiry time.
5. Saves all results incrementally to a CSV file named with the current date.

---

## Features

- Fully automated pagination (scrapes up to 100 pages)
- Captures key fields:
  - RFQ ID
  - Title
  - Buyer Name
  - Buyer Image (if available)
  - Inquiry Time
  - Quotes Left
  - Country
  - Quantity Required (with units, e.g. "10 Piece/Pieces")
  - Email Confirmed / Experienced Buyer / Complete Order via RFQ / Typical Replies / Interactive User badges
  - Inquiry URL
  - Inquiry Date (relative time like "25 minutes before")
  - Scraping Date (when the script runs)
- Headless Chrome support for faster, invisible scraping
- Generates CSV output like:
alibaba_rfq_YYYY-MM-DD.csv

---

## Project Structure

Alibaba_Webscraper/
│
├── alibaba_rfq.py # Main scraping script
├── requirements.txt # Required packages
├── README.md # Project documentation
└── LICENSE # MIT License

---

## How to Run

1. Clone this repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/alibaba_rfq_webscraper.git
   cd alibaba_rfq_webscraper

2. Install required packages:
   ```bash
  pip install -r requirements.txt
  
3. Run the scraper:
   ```bash
   python alibaba_webscraper.py

4. View the results in the generated CSV file:
   Alibaba_rfq_YYYY-MM-DD.csv

---

## Prerequisites

- Python 3.8+
- Google Chrome installed
- ChromeDriver matching your Chrome version
- Internet connection

---

## License

This project is licensed under the MIT License.
