import fitz
from pdf2image import convert_from_bytes
import pytesseract
from openai import OpenAI
import os
from app.models import insurance_rules 
import logging



openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract'
logging.basicConfig(level=logging.INFO)  # You can adjust the level as needed
logger = logging.getLogger(__name__)

def is_image_pdf(file):
    try:
        file.seek(0)
        convert_from_bytes(file.read(), first_page=1, last_page=1)
        return True
    except Exception as e:
        if "pdfinfo" in str(e).lower():
            return True
        raise e

def extract_text_with_ocr(file):
    file.seek(0)
    pdf_images = convert_from_bytes(file.read())
    text = "".join(pytesseract.image_to_string(image) for image in pdf_images)
    return text

def extract_text_from_pdf(file):
    pdf_document = fitz.open(stream=file.read(), filetype='pdf')
    text = "".join(page.get_text() for page in pdf_document)
    return text
    
def get_rules_by_type(insurance_type):
    return [rule for rule in insurance_rules if rule.insurance_type.lower() == insurance_type.lower()]

def compare_claim_with_rules(claim_text, insurance_type):
    # Prepare the prompt for OpenAI
    prompt = f"""
    Objective:
    Compare the following insurance claim form with the rules for the insurance type '{insurance_type}'.

    Claim Form Text:
    {claim_text}

    Rules:
    {insurance_type}

    Instructions:
    Identify any discrepancies between the claim form and the rules. Provide a summary of any issues found.
    """
    
    # Generate the comparison summary using OpenAI
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500
    )
    
    comparison_summary_html = response.choices[0].message.content.strip()
    comparison_summary =  comparison_summary_html.replace("\n", "<br>").replace("\n\n", "<br><br>")
    return comparison_summary

def generate_rule_set_from_pdf(file):
    # Extract text from the uploaded PDF
    text = extract_text_from_pdf(file)
    
    # Prepare the prompt for OpenAI
    prompt = f"""
    Objective:
    Generate a rule set for an insurance policy based on the following text.

    Policy Text:
    {text}

    Instructions:
    Identify and extract the information like:
    - Insurance Type
    - Coverage Limit
    - Deductible
    - Covered Procedures
    - Exclusions
    - Waiting Period,
    [[other important details]]

    Format the output as follows:
    InsuranceRule(
        insurance_type="[[insurance_type]]",
        coverage_limit=[[coverage_limit]],
        deductible=[[deductible]],
        covered_procedures="[[covered_procedures]]",
        exclusions=[[exclusions]],
        waiting_period=[[waiting_period]]
       [[other important details]]
    )
    """
    
    # Generate the rule set using OpenAI
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500
    )
    
    rule_set_html = response.choices[0].message.content.strip()
    rule_set = rule_set_html.replace("\n", "<br>").replace("\n\n", "<br><br>")
    return rule_set

def compare_claim_with_policy(claim_form, policy_doc):
    claimText = extract_text_from_pdf(claim_form)
    rule_set = generate_rule_set_from_pdf(policy_doc)
    comparison_summary = compare_claim_with_rules(claim_text=claimText, insurance_type=rule_set)

    return comparison_summary
