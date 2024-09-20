import os
from flask import Blueprint, request, jsonify, render_template
from .utils import is_image_pdf, extract_text_with_ocr, extract_text_from_pdf, compare_claim_with_rules, generate_rule_set_from_pdf, compare_claim_with_policy
from app.models import insurance_rules

main = Blueprint('main', __name__)


@main.route('/')
def index():
    insurance_types = [rule.insurance_type for rule in insurance_rules]
    return render_template('index.html', insurance_types=insurance_types)

@main.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    
    if not file or not file.filename.endswith('.pdf'):
        return jsonify({'error': 'Invalid file format. Only PDF files are accepted.'}), 400

    pdf_text = extract_text_with_ocr(file) if is_image_pdf(file) else extract_text_from_pdf(file)
    insurance_type = request.form['insurance_type']
    summary = compare_claim_with_rules(pdf_text, insurance_type)
    
    return render_template('result.html', summary=summary)

@main.route('/rule_gen', methods=['POST'])
def generate_rule_set():
    uploaded_file = request.files.get('file')  # Get the uploaded file
    if uploaded_file:
        if uploaded_file.filename == '':
            return "No selected file", 400
        
        # Check if the file is empty
        if uploaded_file.readable():
            uploaded_file.seek(0)  # Reset file pointer to the beginning
            summary = generate_rule_set_from_pdf(uploaded_file)  # Pass the file object
            return render_template('result.html', summary=summary)
        else:
            return "Uploaded file is empty", 400
    return "No file uploaded", 400

@main.route('/compare', methods=['POST'])
def claim_policy_review():
    claim_file = request.files.get('claim_file')  # Get the uploaded file
    policy_file = request.files.get('policy_file')  # Get the uploaded file
    
    # Check if both files are uploaded
    if not claim_file or not policy_file:
        return "No file uploaded", 400

    # Check if the claim file is empty
    if claim_file.filename == '':
        return "No selected claim file", 400

    # Check if the policy file is empty
    if policy_file.filename == '':
        return "No selected policy file", 400

    # Check if the files are readable
    if claim_file.readable() and policy_file.readable():
        claim_file.seek(0)  # Reset file pointer to the beginning
        policy_file.seek(0)  # Reset file pointer to the beginning
        summary = compare_claim_with_policy(claim_form=claim_file, policy_doc=policy_file)  # Pass the file objects
        return render_template('result.html', summary=summary)
    else:
        return "Uploaded file is empty", 400