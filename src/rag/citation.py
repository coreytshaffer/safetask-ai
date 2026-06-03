import requests
from typing import Optional, Dict, Any
from logger import logger

class CrossrefResolver:
    """Resolves paper metadata and formatted citations from Crossref API."""
    
    BASE_URL = "https://api.crossref.org/works"
    
    def __init__(self, email: str = "fieldaware-bot@example.com"):
        # Crossref prefers you send a mailto in the headers for polite pool access
        self.headers = {
            "User-Agent": f"FieldAware/0.1 (mailto:{email})"
        }
        
    def _format_authors(self, authors: list) -> str:
        """Formats the Crossref author list into APA style (approximate)."""
        if not authors:
            return "Unknown Authors"
            
        formatted = []
        for author in authors:
            family = author.get("family", "")
            given = author.get("given", "")
            if family and given:
                formatted.append(f"{family}, {given[0]}.")
            elif family:
                formatted.append(family)
                
        if len(formatted) > 3:
            return f"{formatted[0]} et al."
        elif len(formatted) == 2:
            return f"{formatted[0]} & {formatted[1]}"
        else:
            return ", ".join(formatted)

    def resolve_doi(self, doi: str) -> Optional[Dict[str, Any]]:
        """
        Fetches metadata for a specific DOI.
        Returns a dictionary with formatted citation details, or None if offline/failed.
        """
        try:
            url = f"{self.BASE_URL}/{doi}"
            response = requests.get(url, headers=self.headers, timeout=5)
            response.raise_for_status()
            
            data = response.json().get("message", {})
            return self._parse_crossref_message(data)
            
        except requests.exceptions.RequestException as e:
            logger.warning(f"Crossref API request failed for DOI {doi}. You may be offline. Error: {e}")
            return None
            
    def search_title(self, title: str) -> Optional[Dict[str, Any]]:
        """
        Searches Crossref for a paper title and returns the best match.
        Returns a dictionary with formatted citation details, or None if offline/failed.
        """
        try:
            params = {
                "query.title": title,
                "rows": 1,
                "select": "DOI,title,author,issued,container-title,publisher"
            }
            response = requests.get(self.BASE_URL, headers=self.headers, params=params, timeout=5)
            response.raise_for_status()
            
            items = response.json().get("message", {}).get("items", [])
            if not items:
                logger.info(f"No Crossref results found for title: {title}")
                return None
                
            return self._parse_crossref_message(items[0])
            
        except requests.exceptions.RequestException as e:
            logger.warning(f"Crossref API request failed for title search '{title}'. You may be offline. Error: {e}")
            return None
            
    def _parse_crossref_message(self, item: dict) -> Dict[str, Any]:
        """Parses the raw JSON item from Crossref into our standard citation dict."""
        
        # Extract title
        title_list = item.get("title", [])
        title = title_list[0] if title_list else "Unknown Title"
        
        # Extract year
        issued = item.get("issued", {})
        date_parts = issued.get("date-parts", [[]])
        year = str(date_parts[0][0]) if date_parts and date_parts[0] else "n.d."
        
        # Extract journal
        container_list = item.get("container-title", [])
        journal = container_list[0] if container_list else item.get("publisher", "Unknown Publisher")
        
        # Extract authors
        authors = self._format_authors(item.get("author", []))
        
        # Extract DOI
        doi = item.get("DOI", "")
        doi_url = f"https://doi.org/{doi}" if doi else ""
        
        # Construct approximate APA citation string
        citation_str = f"{authors} ({year}). {title}. {journal}."
        if doi_url:
            citation_str += f" {doi_url}"
            
        return {
            "title": title,
            "authors": authors,
            "year": year,
            "journal": journal,
            "doi": doi,
            "url": doi_url,
            "formatted_citation": citation_str
        }
