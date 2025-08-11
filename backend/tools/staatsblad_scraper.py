#!/usr/bin/env python3
"""
Staatsblad Monitor Scraper
Scrapes Belgian Official Gazette Monitor for company information, financial data, and publications
"""

import requests
import json
import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime
from bs4 import BeautifulSoup
import re
import time

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from scrapers.utils.http_client import HTTPClient
from scrapers.utils.logger import ScraperLogger


class StaatsbladScraper:
    """
    Scraper for Belgian Staatsblad Monitor (Official Gazette Monitor)
    """
    
    def __init__(self):
        self.base_url = "https://staatsbladmonitor.be"
        self.http_client = HTTPClient()
        self.logger = ScraperLogger("staatsblad_monitor")
        
    def search_company(self, company_number: str) -> Dict[str, Any]:
        """
        Search for a company by its company number (ondernemingsnummer)
        
        Args:
            company_number: Company number (e.g., '0403200393')
            
        Returns:
            Dictionary containing all scraped company data
        """
        try:
            self.logger.log_scraping_start(f"staatsblad_search_{company_number}")
            
            # Clean and format the company number
            clean_number = self._clean_company_number(company_number)
            
            # Construct the URL
            url = f"{self.base_url}/bedrijfsfiche.html?ondernemingsnummer={clean_number}"
            
            self.logger.logger.info(f"Searching company {clean_number} at {url}")
            
            # Get the page content
            response = self.http_client.get(url)
            response.raise_for_status()
            
            # Parse the HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract all data
            company_data = self._parse_company_page(soup, clean_number)
            
            self.logger.log_data_extracted(f"staatsblad_search_{clean_number}", {
                "company_name": company_data.get('company_name'),
                "publications_count": len(company_data.get('publications', [])),
                "financial_years_count": len(company_data.get('financial_data', [])),
                "pdf_links_count": len(company_data.get('pdf_links', []))
            })
            
            return {
                'success': True,
                'data': company_data,
                'metadata': {
                    'source': 'Staatsblad Monitor',
                    'country': 'Belgium',
                    'request_time': datetime.now().isoformat(),
                    'company_number_input': company_number,
                    'company_number_clean': clean_number,
                    'url': url
                }
            }
            
        except Exception as e:
            self.logger.log_scraping_error(f"staatsblad_search_{company_number}", str(e))
            return {
                'success': False,
                'error': str(e),
                'data': {
                    'status': 'ERROR',
                    'company_number': company_number
                },
                'metadata': {
                    'source': 'Staatsblad Monitor',
                    'country': 'Belgium',
                    'request_time': datetime.now().isoformat(),
                    'company_number_input': company_number
                }
            }
    
    def _clean_company_number(self, company_number: str) -> str:
        """
        Clean and format company number
        """
        # Remove dots and spaces
        clean = re.sub(r'[.\s]', '', company_number)
        return clean
    
    def _parse_company_page(self, soup: BeautifulSoup, company_number: str) -> Dict[str, Any]:
        """
        Parse the company page and extract all information
        """
        data = {
            'company_number': company_number,
            'scraped_at': datetime.now().isoformat()
        }
        
        # Extract basic company information
        data.update(self._extract_basic_info(soup))
        
        # Extract financial data
        data['financial_data'] = self._extract_financial_data(soup)
        
        # Extract activities
        data['activities'] = self._extract_activities(soup)
        
        # Extract publications
        data['publications'] = self._extract_publications(soup)
        
        # Extract directors info (if available)
        data['directors'] = self._extract_directors(soup)
        
        # Extract PDF links
        data['pdf_links'] = self._extract_pdf_links(soup)
        
        return data
    
    def _extract_basic_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Extract basic company information
        """
        info = {}
        
        try:
            # Company name (usually in a prominent heading)
            name_elem = soup.find('h1') or soup.find('h2') or soup.find('title')
            if name_elem:
                info['company_name'] = name_elem.get_text(strip=True)
            
            # Extract table data for company details
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True).lower()
                        value = cells[1].get_text(strip=True)
                        
                        # Map Dutch keys to English
                        key_mapping = {
                            'vennootschapsnaam': 'company_name',
                            'vennootschapsvorm': 'legal_form',
                            'ondernemingsnummer': 'company_number',
                            'status': 'status',
                            'juridische situatie': 'legal_situation',
                            'adres': 'address',
                            'laatste publicatie': 'last_publication',
                            'laatste jaarrekening': 'last_annual_report'
                        }
                        
                        if key in key_mapping:
                            info[key_mapping[key]] = value
                        else:
                            info[key] = value
            
            # Extract address information
            address_elem = soup.find(string=re.compile(r'Marnixlaan|Brussel|Antwerpen|Gent', re.I))
            if address_elem:
                info['full_address'] = address_elem.strip()
            
        except Exception as e:
            self.logger.logger.warning(f"Error extracting basic info: {str(e)}")
        
        return info
    
    def _extract_financial_data(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extract financial data from the annual reports table
        """
        financial_data = []
        
        try:
            # Look for financial tables
            tables = soup.find_all('table')
            
            for table in tables:
                # Check if this table contains financial data
                headers = table.find_all(['th', 'td'])
                header_text = ' '.join([h.get_text(strip=True) for h in headers[:5]])
                
                if any(keyword in header_text.lower() for keyword in ['activa', 'brutomarge', 'bedrijfswinst', 'eigen vermogen', 'schulden']):
                    rows = table.find_all('tr')
                    
                    for row in rows[1:]:  # Skip header row
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 6:
                            try:
                                financial_year = {
                                    'year_end': cells[0].get_text(strip=True),
                                    'assets': cells[1].get_text(strip=True),
                                    'gross_margin': cells[2].get_text(strip=True),
                                    'operating_profit': cells[3].get_text(strip=True),
                                    'taxes': cells[4].get_text(strip=True),
                                    'equity': cells[5].get_text(strip=True),
                                    'debts': cells[6].get_text(strip=True) if len(cells) > 6 else ''
                                }
                                financial_data.append(financial_year)
                            except IndexError:
                                continue
        
        except Exception as e:
            self.logger.logger.warning(f"Error extracting financial data: {str(e)}")
        
        return financial_data
    
    def _extract_activities(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extract company activities (NACE codes)
        """
        activities = []
        
        try:
            # Look for activities section
            activities_section = soup.find(string=re.compile(r'Activiteiten|NACE', re.I))
            if activities_section:
                parent = activities_section.parent
                if parent:
                    # Find all activity items
                    activity_items = parent.find_all_next('li', limit=10)  # Limit to avoid going too far
                    
                    for item in activity_items:
                        activity_text = item.get_text(strip=True)
                        if activity_text and not activity_text.startswith('('):
                            activities.append({
                                'activity': activity_text,
                                'nace_code': self._extract_nace_code(activity_text)
                            })
        
        except Exception as e:
            self.logger.logger.warning(f"Error extracting activities: {str(e)}")
        
        return activities
    
    def _extract_nace_code(self, activity_text: str) -> Optional[str]:
        """
        Extract NACE code from activity text
        """
        # Look for NACE code pattern
        nace_match = re.search(r'\((\d{4,5})\)', activity_text)
        if nace_match:
            return nace_match.group(1)
        return None
    
    def _extract_publications(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extract Official Gazette publications
        """
        publications = []
        
        try:
            # Look for publications section
            publications_section = soup.find(string=re.compile(r'Publicaties Belgisch Staatsblad', re.I))
            if publications_section:
                parent = publications_section.parent
                if parent:
                    # Find all publication entries
                    publication_entries = parent.find_all_next(['tr', 'li'], limit=200)  # Limit to avoid going too far
                    
                    for entry in publication_entries:
                        entry_text = entry.get_text(strip=True)
                        
                        # Look for date and type pattern
                        date_type_match = re.search(r'(\d{2}-\d{2}-\d{4})\s+(.+)', entry_text)
                        if date_type_match:
                            publications.append({
                                'date': date_type_match.group(1),
                                'type': date_type_match.group(2).strip(),
                                'full_text': entry_text
                            })
        
        except Exception as e:
            self.logger.logger.warning(f"Error extracting publications: {str(e)}")
        
        return publications
    
    def _extract_directors(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Extract directors information (usually requires registration)
        """
        directors_info = {
            'available': False,
            'requires_registration': True,
            'message': 'Directors information requires registration'
        }
        
        try:
            # Check if directors section exists and is accessible
            directors_section = soup.find(string=re.compile(r'Bestuurders|Directors', re.I))
            if directors_section:
                parent = directors_section.parent
                if parent:
                    # Check if there's a registration message
                    registration_msg = parent.find(string=re.compile(r'Enkel toegankelijk voor geregistreerde gebruikers|Only accessible for registered users', re.I))
                    if registration_msg:
                        directors_info['message'] = 'Directors information requires registration'
                    else:
                        # Try to extract actual directors
                        directors_list = parent.find_all(['li', 'tr'])
                        if directors_list:
                            directors_info['available'] = True
                            directors_info['directors'] = [d.get_text(strip=True) for d in directors_list if d.get_text(strip=True)]
        
        except Exception as e:
            self.logger.logger.warning(f"Error extracting directors: {str(e)}")
        
        return directors_info
    
    def _extract_pdf_links(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extract PDF links from the page
        """
        pdf_links = []
        
        try:
            # Look for PDF links in various formats
            pdf_patterns = [
                r'\.pdf$',  # Direct PDF links
                r'jaarrekening',  # Annual reports
                r'financial',  # Financial documents
                r'statement',  # Financial statements
                r'verslag',  # Reports
                r'publicatie',  # Publications
            ]
            
            # Find all links
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link.get('href', '').lower()
                link_text = link.get_text(strip=True).lower()
                
                # Check if it's a PDF link
                is_pdf = any(re.search(pattern, href) for pattern in pdf_patterns) or \
                         any(re.search(pattern, link_text) for pattern in pdf_patterns) or \
                         href.endswith('.pdf')
                
                if is_pdf:
                    # Make URL absolute if it's relative
                    if href.startswith('/'):
                        full_url = f"{self.base_url}{href}"
                    elif href.startswith('http'):
                        full_url = href
                    else:
                        full_url = f"{self.base_url}/{href}"
                    
                    pdf_info = {
                        'title': link.get_text(strip=True),
                        'url': full_url,
                        'filename': self._extract_filename_from_url(full_url),
                        'type': self._classify_pdf_type(link_text, href)
                    }
                    pdf_links.append(pdf_info)
            
            # Also look for PDF links in text content
            text_content = soup.get_text()
            pdf_urls = re.findall(r'https?://[^\s]+\.pdf', text_content)
            
            for url in pdf_urls:
                if url not in [pdf['url'] for pdf in pdf_links]:
                    pdf_info = {
                        'title': f"PDF Document - {self._extract_filename_from_url(url)}",
                        'url': url,
                        'filename': self._extract_filename_from_url(url),
                        'type': self._classify_pdf_type('', url)
                    }
                    pdf_links.append(pdf_info)
        
        except Exception as e:
            self.logger.logger.warning(f"Error extracting PDF links: {str(e)}")
        
        return pdf_links
    
    def _extract_filename_from_url(self, url: str) -> str:
        """
        Extract filename from URL
        """
        try:
            # Extract filename from URL
            filename = url.split('/')[-1]
            # Remove query parameters
            filename = filename.split('?')[0]
            # Ensure it has .pdf extension
            if not filename.endswith('.pdf'):
                filename += '.pdf'
            return filename
        except:
            return f"document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    def _classify_pdf_type(self, link_text: str, url: str) -> str:
        """
        Classify PDF type based on link text and URL
        """
        text_lower = link_text.lower()
        url_lower = url.lower()
        
        if any(keyword in text_lower or keyword in url_lower for keyword in ['jaarrekening', 'annual', 'financial']):
            return 'annual_report'
        elif any(keyword in text_lower or keyword in url_lower for keyword in ['statuten', 'articles', 'constitution']):
            return 'articles_of_association'
        elif any(keyword in text_lower or keyword in url_lower for keyword in ['publicatie', 'publication', 'gazette']):
            return 'official_publication'
        elif any(keyword in text_lower or keyword in url_lower for keyword in ['verslag', 'report']):
            return 'report'
        elif any(keyword in text_lower or keyword in url_lower for keyword in ['balans', 'balance']):
            return 'balance_sheet'
        else:
            return 'document'
    
    def save_results_to_files(self, data: Dict[str, Any], filename_prefix: str = "staatsblad") -> None:
        """
        Save results to JSON, Markdown, and TXT files
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create results directory if it doesn't exist
            os.makedirs('results', exist_ok=True)
            
            # Save as JSON
            json_filename = f"results/{filename_prefix}_{timestamp}.json"
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Save as Markdown
            md_filename = f"results/{filename_prefix}_{timestamp}.md"
            with open(md_filename, 'w', encoding='utf-8') as f:
                f.write(self._format_markdown(data))
            
            # Save as TXT
            txt_filename = f"results/{filename_prefix}_{timestamp}.txt"
            with open(txt_filename, 'w', encoding='utf-8') as f:
                f.write(self._format_text(data))
            
            self.logger.logger.info(f"Results saved to {json_filename}, {md_filename}, {txt_filename}")
            
        except Exception as e:
            self.logger.logger.error(f"Error saving results: {str(e)}")
    
    def _format_markdown(self, data: Dict[str, Any]) -> str:
        """
        Format data as Markdown
        """
        md = []
        
        if data.get('success'):
            company_data = data.get('data', {})
            
            md.append(f"# {company_data.get('company_name', 'Company Information')}")
            md.append(f"*Scraped from Staatsblad Monitor on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
            md.append("")
            
            # Basic Information
            md.append("## Company Information")
            md.append("")
            for key, value in company_data.items():
                if key not in ['financial_data', 'activities', 'publications', 'directors']:
                    md.append(f"**{key.replace('_', ' ').title()}**: {value}")
            md.append("")
            
            # Financial Data
            if company_data.get('financial_data'):
                md.append("## Financial Data")
                md.append("")
                md.append("| Year End | Assets | Gross Margin | Operating Profit | Taxes | Equity | Debts |")
                md.append("|----------|--------|--------------|------------------|-------|--------|-------|")
                for year in company_data['financial_data']:
                    md.append(f"| {year.get('year_end', '')} | {year.get('assets', '')} | {year.get('gross_margin', '')} | {year.get('operating_profit', '')} | {year.get('taxes', '')} | {year.get('equity', '')} | {year.get('debts', '')} |")
                md.append("")
            
            # Activities
            if company_data.get('activities'):
                md.append("## Activities")
                md.append("")
                for activity in company_data['activities']:
                    md.append(f"- {activity.get('activity', '')} {activity.get('nace_code', '')}")
                md.append("")
            
            # Publications
            if company_data.get('publications'):
                md.append("## Official Gazette Publications")
                md.append("")
                md.append("| Date | Type |")
                md.append("|------|------|")
                for pub in company_data['publications'][:50]:  # Limit to first 50
                    md.append(f"| {pub.get('date', '')} | {pub.get('type', '')} |")
                md.append("")
                if len(company_data['publications']) > 50:
                    md.append(f"*... and {len(company_data['publications']) - 50} more publications*")
                md.append("")
            
            # Directors
            if company_data.get('directors'):
                directors = company_data['directors']
                md.append("## Directors")
                md.append("")
                if directors.get('available'):
                    for director in directors.get('directors', []):
                        md.append(f"- {director}")
                else:
                    md.append(f"*{directors.get('message', 'Directors information not available')}*")
                md.append("")
            
            # PDF Links
            if company_data.get('pdf_links'):
                md.append("## PDF Documents")
                md.append("")
                md.append("| Title | Type | URL |")
                md.append("|-------|------|-----|")
                for pdf in company_data['pdf_links']:
                    md.append(f"| {pdf.get('title', 'Unknown')} | {pdf.get('type', 'document')} | {pdf.get('url', 'N/A')} |")
                md.append("")
        
        else:
            md.append("# Error")
            md.append(f"**Error**: {data.get('error', 'Unknown error')}")
        
        return "\n".join(md)
    
    def _format_text(self, data: Dict[str, Any]) -> str:
        """
        Format data as plain text
        """
        lines = []
        
        if data.get('success'):
            company_data = data.get('data', {})
            
            lines.append(f"STAATSBALD MONITOR - COMPANY REPORT")
            lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append("=" * 50)
            lines.append("")
            
            # Basic Information
            lines.append("COMPANY INFORMATION:")
            lines.append("-" * 20)
            for key, value in company_data.items():
                if key not in ['financial_data', 'activities', 'publications', 'directors']:
                    lines.append(f"{key.replace('_', ' ').title()}: {value}")
            lines.append("")
            
            # Financial Data
            if company_data.get('financial_data'):
                lines.append("FINANCIAL DATA:")
                lines.append("-" * 15)
                for year in company_data['financial_data']:
                    lines.append(f"Year: {year.get('year_end', '')}")
                    lines.append(f"  Assets: {year.get('assets', '')}")
                    lines.append(f"  Gross Margin: {year.get('gross_margin', '')}")
                    lines.append(f"  Operating Profit: {year.get('operating_profit', '')}")
                    lines.append(f"  Taxes: {year.get('taxes', '')}")
                    lines.append(f"  Equity: {year.get('equity', '')}")
                    lines.append(f"  Debts: {year.get('debts', '')}")
                    lines.append("")
            
            # Activities
            if company_data.get('activities'):
                lines.append("ACTIVITIES:")
                lines.append("-" * 10)
                for activity in company_data['activities']:
                    lines.append(f"- {activity.get('activity', '')} {activity.get('nace_code', '')}")
                lines.append("")
            
            # Publications
            if company_data.get('publications'):
                lines.append("PUBLICATIONS:")
                lines.append("-" * 12)
                for pub in company_data['publications'][:20]:  # Limit to first 20
                    lines.append(f"{pub.get('date', '')} - {pub.get('type', '')}")
                if len(company_data['publications']) > 20:
                    lines.append(f"... and {len(company_data['publications']) - 20} more")
                lines.append("")
            
            # PDF Documents
            if company_data.get('pdf_links'):
                lines.append("PDF DOCUMENTS:")
                lines.append("-" * 15)
                for pdf in company_data['pdf_links']:
                    lines.append(f"- {pdf.get('title', 'Unknown')} ({pdf.get('type', 'document')})")
                    lines.append(f"  URL: {pdf.get('url', 'N/A')}")
                lines.append("")
        
        else:
            lines.append("ERROR:")
            lines.append(f"{data.get('error', 'Unknown error')}")
        
        return "\n".join(lines)
    
    def close(self):
        """Close the scraper and cleanup"""
        self.logger.close() 