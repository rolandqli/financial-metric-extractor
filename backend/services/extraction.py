import json
import os
import re
from typing import Any

import pdfplumber
import spacy
from fastapi import UploadFile
from openai import OpenAI
from tqdm import tqdm
from dotenv import load_dotenv
from utils import transform_data, valid_table
from logging_config import logger

load_dotenv()

# Initialize shared clients/models once at import time
client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))
nlp = spacy.load("en_core_web_sm")

# Target pattern for filtering relevant sentences
PATTERN = r"\$|gross|million|billion|%"


def extract_metrics(file: UploadFile) -> dict[str, Any]:
    """
    Given a PDF file, extract all requested metrics using the LLM.

    :param file: PDF file uploaded via FastAPI
    :type file: UploadFile
    :return: Parsed and transformed metrics
    :rtype: dict[str, Any]
    """
    logger.info(f"Started extraction for file: {file.filename}")
    input_text: list[str] = []

    # Extract relevant text and tables from PDF file
    with pdfplumber.open(file.file) as pdf:
        pdf_metadata = pdf.metadata

        for i, page in tqdm(enumerate(pdf.pages)):
            # Extract text and segment sentences
            page_text = page.extract_text()
            doc = nlp(page_text)

            # Always include first 3 lines as this usually includes company name and quarter
            if i == 0:
                input_text.extend(
                    [sent.text.strip() for sent in list(doc.sents)[:3]]
                )

            # Filter sentences by pattern
            relevant_sentences = [
                sent.text.strip()
                for sent in doc.sents
                if re.search(PATTERN, sent.text)
            ]
            input_text.extend(relevant_sentences)

            # Detect and extract tables
            if page.find_tables():
                tables = page.extract_tables()
                for table in tables:
                    # Do not add detected tables that are mostly empty
                    if valid_table(table):
                        input_text.append(str(table))

    # Join all sentences and tables
    transcript = "\n".join(input_text)

    # Add metadata (helps with company name and quarter)
    metadata: dict[str, Any] = {}
    author = pdf_metadata.get("Author")
    title = pdf_metadata.get("Title")
    if author:
        metadata["Author"] = author
    if title:
        metadata["Title"] = title

    # Setup input
    all_info = str(metadata) + transcript
    content = [
        {
            "role": "user",
            "content": f"""
        You are a financial data extraction assistant.

        Given the following earnings call transcript or deck, extract the requested financial metrics.
        Instructions:
        - Extract values only if they are explicitly stated in the text.
        - Do NOT infer missing metrics. You are allowed to calculate gross margin and operating income if relevant metrics are present.
        - If operating income is missing, calculate as total revenue - cost of revenue/COGS - operating expenses or gross profit - operating expenses, ONLY if these metrics are explicitly stated.
        - If gross margin is missing, calculate as gross profit = total revenue - cost of revenue, ONLY if these metrics are explicitly stated. Calculate cost of revenue as revenue - operational income - operational expense.
        - Make sure that the order of magnitude of each metric is correct (million, billion)
        - Total expenses and expenses that are a part of operational expenses (R&D, SG&A, etc.) are NOT operational expenses.
        - If a metric is not present or unclear, return null.
        - Normalize all monetary values to numbers in USD.
        - If 3 of [total_revenue, operating_income, gross_margin, operating_expenses] are present, fill in the remaining one accordingly
        - Losses are always expressed as negative (net_loss: -200M)
        - Gross margin, YoY and QoQ should be a percentage number (e.g., 42.5).
        - Quarter should be in the format: "Q(number) (year)" (e.g., "Q3 2024").
        - Bracketed text represents a table. Occasionally, some tables appear as plain text (i.e. Total revenues $ 1,300.2 $ 1,348.8 (3.6) % $ 3,560.6 $ 3,330.8 6.9). Treat the first entry in each row as the metric name, and the rest as values associated with that metric. Make sure to know the order of magnitude of each table, if unsure don't use info.
        - Make sure metrics are not for segments.
        - Ensure all metrics are for the relevant quarter, not a different quarter and not the year.
        - Report combined_buybacks_and_dividends only if buybacks and dividends aren't reported separately, but a combined total is.
        - Based on the metrics extracted, the performance metric is a number from -5 to 5 representing over/under performance on the quarter. Also use YoY and QoQ for relevant metrics and net income margin.
        - Output JSON only. No explanations.
        {{
        "company_name": string | null,
        "quarter": string | null,
        "total_revenue": {{
            "value": "number | null",
            "yoy": "number | null",
            "qoq": "number | null"
         }},
        "earnings_per_share": {{
            "value": "number | null",
            "yoy": "number | null",
            "qoq": "number | null"
         }},
        "net_income": {{
            "value": "number | null",
            "yoy": "number | null",
            "qoq": "number | null"
         }},
        "net_loss": "number | null",
        "operating_income": {{
            "value": "number | null",
            "yoy": "number | null",
            "qoq": "number | null"
         }},
        "operating_loss": "number | null",
        "gross_margin": {{
            "value": "number | null",
            "yoy": "number | null",
            "qoq": "number | null"
         }},
        "operating_expenses": {{
            "value": "number | null",
            "yoy": "number | null",
            "qoq": "number | null"
         }},
        "buybacks_and_dividends" : {{
            "buybacks": "number | null",
            "dividends": "number | null",
            "combined": "number | null"
         }},
        "performance": "number | null"
        }}

        Input text:
        {all_info}
        """,
        },
    ]

    # Get JSON from response
    response = client.responses.create(
        model="gpt-5-nano",
        input=content,
    )
    texts: list[str] = []
    for item in response.output:
        if getattr(item, "content", None):
            for c in item.content:
                if getattr(c, "text", None):
                    texts.append(c.text)
    data = json.loads(texts[0])

    # Transform data to be more human readable
    transform_data(data)

    return data

