import urllib.request
import xml.etree.ElementTree as ET
import json
import os
import os

# arXiv API configuration
BASE_URL = "http://export.arxiv.org/api/query?"
# Categories as per assignment requirements
CATEGORIES = ["cs.AI", "cs.CV", "cs.SE", "cs.TH", "cs.SY", "cs.LG", "cs.CL", "cs.NE", "cs.RO", "cs.GT", "cs.MM"]
MAX_RESULTS = 10  # Fetch 10 papers per category

def fetch_arxiv_papers(category, max_results):
    """Fetch real papers from arXiv for a specific category"""
    # Construct the query URL
    url = f"{BASE_URL}search_query=cat:{category}&sortBy=submittedDate&sortOrder=descending&max_results={max_results}"
    
    try:
        with urllib.request.urlopen(url) as response:
            data = response.read().decode('utf-8')
        
        # Parse XML response from arXiv
        root = ET.fromstring(data)
        namespace = {'atom': 'http://www.w3.org/2005/Atom'}
        papers = []
        
        for entry in root.findall('atom:entry', namespace):
            # 1. Extract basic metadata
            entry_id = entry.find('atom:id', namespace).text
            title = entry.find('atom:title', namespace).text.replace('\n', ' ').strip()
            published = entry.find('atom:published', namespace).text
            authors = [author.find('atom:name', namespace).text for author in entry.findall('atom:author', namespace)]
            
            # --- New Feature: Handle PDF Link (Assignment Req) ---
            # arXiv ID link is usually http://arxiv.org/abs/xxxx
            # PDF link is usually http://arxiv.org/pdf/xxxx
            pdf_link = entry_id.replace("/abs/", "/pdf/")
            
            # --- New Feature: Generate BibTeX (Assignment Req) ---
            year = published[:4]
            first_author_lastname = authors[0].split()[-1] if authors else "Unknown"
            # Remove non-alphabetic chars from the first word of the title for the key
            title_first_word = ''.join(filter(str.isalpha, title.split()[0]))
            citation_key = f"{first_author_lastname}{year}{title_first_word}"
            
            # Construct standard BibTeX string
            bibtex = (
                f"@article{{{citation_key}}},\n"
                f"  title={{{title}}},\n"
                f"  author={{{' and '.join(authors)}}},\n"
                f"  journal={{arXiv preprint arXiv:{entry_id.split('/')[-1]}}},\n"
                f"  year={{{year}}},\n"
                f"  url={{{entry_id}}}\n"
                f"}}"
            )
            paper = {
                'title': title,
                'published': published,
                'updated': entry.find('atom:updated', namespace).text,
                'summary': entry.find('atom:summary', namespace).text.replace('\n', ' ').strip(),
                'link': entry_id,       # Original Abstract Page Link
                'pdf_link': pdf_link,   # Direct PDF Link
                'bibtex': bibtex,       # Citation String
                'authors': authors,
                'categories': [cat.get('term') for cat in entry.findall('atom:category', namespace)]
            }
            papers.append(paper)
        
        return papers
    except Exception as e:
        print(f"Error fetching papers for category {category}: {str(e)}")
        return []

def main():
    """Main function to fetch papers from all categories and save to JSON"""
    all_papers = []
    
    print("Starting data fetch...")
    for category in CATEGORIES:
        print(f"Fetching papers for category: {category}")
        papers = fetch_arxiv_papers(category, MAX_RESULTS)
        all_papers.extend(papers)
        print(f"Fetched {len(papers)} papers for category: {category}")
    
    # --- Locate directory relative to this script ---
    # This ensures papers.json is always saved in 'workspace/' alongside data_fetcher.py
    script_dir = os.path.dirname(os.path.abspath(__file__))
    save_dir = os.path.join(script_dir, 'workspace')
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, 'papers.json')
    
    # Save to papers.json
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(all_papers, f, indent=2, ensure_ascii=False)
    
    print(f"Papers saved to: {save_path}")
    
    print(f"\nTotal papers fetched: {len(all_papers)}")
    print(f"Papers saved to: papers.json")

if __name__ == "__main__":
    main()