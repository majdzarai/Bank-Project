from langchain_ollama import ChatOllama
from tools.vat_tool import validate_vat_tool
import json
from datetime import datetime

def validate_vat(country_code: str, vat_number: str) -> str:
    try:
        # Call VAT tool
        input_data = json.dumps({"country_code": country_code.upper(), "vat_number": vat_number})
        result = validate_vat_tool(input_data)
        
        # Enhanced LLM formatting for professional output
        llm = ChatOllama(model="llama3.1", temperature=0.1)
        
        prompt = f"""
You are a professional business compliance analyst. Create a comprehensive VAT validation report.

VAT Details:
- Country: {country_code.upper()}
- VAT Number: {vat_number}
- Validation Data: {result}

Format as a professional business report with:
1. Executive Summary
2. Validation Status (VALID/INVALID with clear indicators)
3. Company Information (if available)
4. Compliance Assessment
5. Recommendations
6. Technical Details

Use professional business language, clear formatting, and include relevant compliance insights.
"""
        
        response = llm.invoke(prompt)
        
        # Add professional header and footer
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        professional_output = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                          VAT VALIDATION REPORT                              ║
║                        Agent: VAT Compliance Validator                      ║
║                        Generated: {timestamp}                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

{response.content}

╔══════════════════════════════════════════════════════════════════════════════╗
║ AGENT STATUS: ✅ VAT VALIDATION COMPLETE                                    ║
║ NEXT STEPS: Ready for Research Agent or Planning Agent integration          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
        
        return professional_output
        
    except Exception as e:
        return f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                          VAT VALIDATION ERROR                               ║
║                        Agent: VAT Compliance Validator                      ║
║                        Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

❌ VALIDATION FAILED

Country Code: {country_code}
VAT Number: {vat_number}
Error: {str(e)}

RECOMMENDATIONS:
- Verify input format
- Check network connectivity
- Ensure VAT number is valid for the specified country

╔══════════════════════════════════════════════════════════════════════════════╗
║ AGENT STATUS: ❌ VAT VALIDATION FAILED                                      ║
║ NEXT STEPS: Fix input and retry before proceeding to other agents           ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""