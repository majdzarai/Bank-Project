from agents.vat_validation_agent import validate_vat

def main():
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                 MULTI-AGENT SYSTEM v1.0                     ║")
    print("║                VAT Validation Agent (Base)                   ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print("\n🤖 This is your foundation agent for the multi-agent system.")
    print("📋 After VAT validation, you can integrate Research & Planning agents.")
    print("\n" + "═" * 60)
    
    # Get user input with validation
    while True:
        country_code = input("\n🌍 Enter EU country code (e.g., BE, FR, DE): ").strip().upper()
        if len(country_code) == 2 and country_code.isalpha():
            break
        print("❌ Invalid format. Please enter exactly 2 letters.")
    
    while True:
        vat_number = input("🔢 Enter VAT number: ").strip()
        if vat_number:
            break
        print("❌ VAT number cannot be empty.")
    
    print("\n🚀 Initializing VAT Validation Agent...")
    print("🔍 Processing validation request...")
    
    # Call agent and get professional result
    result = validate_vat(country_code, vat_number)
    
    print(result)
    
    print("\n" + "═" * 60)
    print("🎯 AGENT SYSTEM STATUS:")
    print("✅ VAT Validation Agent: OPERATIONAL")
    print("⏳ Research Agent: PENDING INTEGRATION")
    print("⏳ Planning Agent: PENDING INTEGRATION")
    print("\n💡 Your foundation agent is ready for multi-agent expansion!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Agent system shutdown initiated.")
    except Exception as e:
        print(f"\n💥 System Error: {str(e)}")