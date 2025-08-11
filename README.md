# Multi-Agent System Backend

A modular, AI-powered backend system for business compliance and validation operations, built with Python and LangChain.

## 🏗️ Architecture Overview

The backend follows a **multi-agent architecture** pattern with the following components:

```
backend/
├── main.py                    # CLI entry point
├── agents/                    # AI agent implementations
│   └── vat_validation_agent.py
├── tools/                     # Core business logic tools
│   ├── vat_tool.py           # EU VAT validation service
│   └── staatsblad_scraper.py # Belgian company data scraper
└── requirements.txt           # Python dependencies
```

## 🤖 Agents

### VAT Validation Agent (`agents/vat_validation_agent.py`)
- **Purpose**: Validates EU VAT numbers and generates professional compliance reports
- **Features**:
  - Real-time VAT validation via EU VIES service
  - AI-powered report generation using LangChain + Ollama
  - Professional business formatting
  - Error handling and recommendations

### Future Agents (Planned)
- Research Agent: Company background investigation
- Planning Agent: Compliance strategy recommendations

## 🛠️ Tools

### VAT Tool (`tools/vat_tool.py`)
- **Function**: EU VAT number validation
- **Service**: Official EU VIES (VAT Information Exchange System)
- **Input**: Country code + VAT number
- **Output**: Validation status, company details, timestamp

### Staatsblad Scraper (`tools/staatsblad_scraper.py`)
- **Function**: Belgian company data extraction
- **Source**: Staatsblad Monitor (Official Gazette)
- **Data**: Company info, financial data, publications, directors
- **Output**: Structured JSON, Markdown, and text formats

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Ollama with Llama 3.1 model
- Internet connection for VAT validation

### Installation

1. **Clone and navigate to backend:**
   ```bash
   cd backend
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start Ollama service:**
   ```bash
   ollama serve
   ```

4. **Pull Llama model:**
   ```bash
   ollama pull llama3.1
   ```

### Usage

#### CLI Mode
```bash
python main.py
```

**Example Session:**
```
🌍 Enter EU country code (e.g., BE, FR, DE): BE
🔢 Enter VAT number: 0403200393
```

#### Programmatic Usage
```python
from agents.vat_validation_agent import validate_vat

# Validate VAT number
result = validate_vat("BE", "0403200393")
print(result)
```

## 📋 API Reference

### VAT Validation Agent

```python
def validate_vat(country_code: str, vat_number: str) -> str
```

**Parameters:**
- `country_code`: 2-letter EU country code (e.g., "BE", "FR", "DE")
- `vat_number`: VAT number to validate

**Returns:**
- Professional business report in formatted text
- Includes validation status, company details, and recommendations

### VAT Tool

```python
def validate_vat_tool(input_data: str) -> str
```

**Input:** JSON string with `country_code` and `vat_number`
**Output:** JSON response with validation results

### Staatsblad Scraper

```python
class StaatsbladScraper:
    def search_company(self, company_number: str) -> Dict[str, Any]
    def save_results_to_files(self, data: Dict[str, Any], filename_prefix: str = "staatsblad")
```

**Features:**
- Company search by business number
- Financial data extraction
- Publication history
- Director information
- PDF document links
- Multiple output formats (JSON, Markdown, Text)

## 🔧 Configuration

### Environment Variables
```bash
# Optional: Custom Ollama endpoint
OLLAMA_BASE_URL=http://localhost:11434

# Optional: Custom model
OLLAMA_MODEL=llama3.1
```

### Model Configuration
The system uses Ollama with Llama 3.1 by default. You can modify the model in `vat_validation_agent.py`:

```python
llm = ChatOllama(model="llama3.1", temperature=0.1)
```

## 🧪 Testing

### Manual Testing
```bash
# Test VAT validation
python -c "from agents.vat_validation_agent import validate_vat; print(validate_vat('BE', '0403200393'))"

# Test scraper
python -c "from tools.staatsblad_scraper import StaatsbladScraper; s = StaatsbladScraper(); print(s.search_company('0403200393'))"
```

### Integration Testing
The system integrates with:
- EU VIES VAT validation service
- Belgian Staatsblad Monitor
- Ollama LLM service

## 📊 Data Flow

```
User Input → Main CLI → Agent Selection → Tool Execution → LLM Processing → Formatted Output
```

1. **Input Validation**: Country code and VAT number format checking
2. **Tool Execution**: VAT validation via EU service or company scraping
3. **LLM Enhancement**: Professional report generation using LangChain
4. **Output Formatting**: Business-ready reports with clear status indicators

## 🚨 Error Handling

The system includes comprehensive error handling:
- Input validation with user-friendly messages
- Network connectivity checks
- Service availability monitoring
- Graceful degradation with error recommendations

## 🔮 Future Enhancements

### Planned Features
- **Research Agent**: Company background investigation
- **Planning Agent**: Compliance strategy recommendations
- **Risk Assessment**: Automated risk scoring
- **API Endpoints**: RESTful API for web integration
- **Database Integration**: Persistent storage for validation history
- **Multi-language Support**: Internationalization

### Architecture Improvements
- **Agent Communication**: Inter-agent messaging system
- **Workflow Orchestration**: Complex multi-step processes
- **Performance Monitoring**: Metrics and health checks
- **Security**: API key management and rate limiting

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Implement changes with tests
4. Submit a pull request

### Code Standards
- Follow PEP 8 style guidelines
- Include type hints for all functions
- Add comprehensive error handling
- Document complex business logic

## 📄 License

This project is part of a multi-agent business compliance system.

## 🆘 Support

For issues and questions:
1. Check the error logs in the output
2. Verify Ollama service is running
3. Ensure internet connectivity for VAT validation
4. Review the configuration settings

---

**System Status**: ✅ Foundation Agent Operational  
**Next Phase**: Research Agent Integration 