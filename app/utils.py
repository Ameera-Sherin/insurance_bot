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
    Rigorously compare the following insurance claim form with the policy rules for the insurance type '{insurance_type}'.

    Claim Form Text:
    {claim_text}

    Rules:
    {insurance_type}

    Instructions:
    Identify and extract the following information from the policy:
    - Insurance Type
    - Coverage Limit
    - Deductible
    - Covered Procedures
    - Exclusions (pay extra attention to any exclusions relevant to the claim condition or procedure)
    - Waiting Period
    [[other important details]]

    **Strictly** evaluate the insurance claim based on this policy to avoid any false positives. If the claim is accepted, it must meet all policy terms. Provide a detailed breakdown of the claim, including:
    - Total Claimed Amount
    - Deductible Applied
    - Amount Approved for Coverage
    - Any Co-payments or Out-of-Pocket Expenses
    - Diagnosis
    - Treatment Plan

    **Ensure all exclusions are properly evaluated**. If any part of the claimed procedure or condition is excluded, the claim should be rejected. Provide the following details in case of a rejection:
    - Reason for Rejection: Clearly state the exclusion(s) that apply to the claimed procedure or condition, referencing the policy's exclusions section.
    
    **Ensure that claims are not Unnecessarily rejected**
    
    If the claim is accepted, list the inclusions and exclusions **specific to the claim condition or procedure**:
    - Inclusions (covered procedures or services related to the claim)
    - Exclusions (services or treatments not covered for this condition)

    Format the output in a readable form as follows:

    Claim Status: [[Accepted/Rejected]]

    If the claim is accepted, provide the following details:
    - Total Claimed Amount: [[total_claimed_amount]]
    - Deductible Applied: [[deductible_applied]]
    - Amount Approved for Coverage: [[amount_approved_for_coverage]]
    - Co-pay/Out-of-Pocket Expenses: [[co_pay_or_out_of_pocket_expenses]]
    - Diagnosis: [[diagnosis]]
    - Treatment Plan: [[treatment_plan]]
    - Inclusions (based on claim condition/disease): [[inclusions]]
    - Exclusions (based on claim condition/disease): [[exclusions]]
    
    If the claim is rejected, provide the following:
    - Reason for Rejection: [[rejection_reason]] (specifically linking to policy exclusions)
    
    Additionally, extract the core policy information:

    Insurance Policy Information:
    - Insurance Type: [[insurance_type]]
    - Coverage Limit: [[coverage_limit]]
    - Deductible: [[deductible]]
    - Covered Procedures: [[covered_procedures]]
    - Exclusions: [[exclusions]]
    - Waiting Period: [[waiting_period]]
    [[other important details]]

    Important: Ensure exclusions are fully considered. Avoid false positives and ensure that any claim approved strictly adheres to the policy terms and conditions.
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
        model="gpt-4o-mini",
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
