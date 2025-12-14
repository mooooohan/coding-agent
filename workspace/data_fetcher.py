import urllib.request
import xml.etree.ElementTree as ET
import json

# arXiv API configuration
BASE_URL = "http://export.arxiv.org/api/query?"
CATEGORIES = ["cs.AI", "cs.CV", "cs.SE", "cs.TH", "cs.SY", "cs.LG", "cs.CL", "cs.NE", "cs.RO", "cs.GT", "cs.MM"]
MAX_RESULTS = 10  # Fetch 10 papers per category

def fetch_arxiv_papers(category, max_results):
    """Fetch real papers from arXiv for a specific category"""
    url = f"{BASE_URL}search_query=cat:{category}&sortBy=submittedDate&sortOrder=descending&max_results={max_results}"
    
    try:
        with urllib.request.urlopen(url) as response:
            data = response.read().decode('utf-8')
        
        # Parse XML response
        root = ET.fromstring(data)
        namespace = {'atom': 'http://www.w3.org/2005/Atom'}
        papers = []
        
        for entry in root.findall('atom:entry', namespace):
            paper = {
                'title': entry.find('atom:title', namespace).text.replace('\n', ' ').strip(),
                'published': entry.find('atom:published', namespace).text,
                'updated': entry.find('atom:updated', namespace).text,
                'summary': entry.find('atom:summary', namespace).text.replace('\n', ' ').strip(),
                'link': entry.find('atom:id', namespace).text,
                'authors': [author.find('atom:name', namespace).text for author in entry.findall('atom:author', namespace)],
                'categories': [category.get('term') for category in entry.findall('atom:category', namespace)]
            }
            papers.append(paper)
        
        return papers
    except Exception as e:
        print(f"Error fetching papers for category {category}: {str(e)}")
        return []

def main():
    """Main function to fetch papers from all categories and save to JSON"""
    all_papers = []
    
    for category in CATEGORIES:
        print(f"Fetching papers for category: {category}")
        papers = fetch_arxiv_papers(category, MAX_RESULTS)
        all_papers.extend(papers)
        print(f"Fetched {len(papers)} papers for category: {category}")
    
    # Save to papers.json
    with open('papers.json', 'w', encoding='utf-8') as f:
        json.dump(all_papers, f, indent=2, ensure_ascii=False)
    
    print(f"\nTotal papers fetched: {len(all_papers)}")
    print(f"Papers saved to: papers.json")

if __name__ == "__main__":
    main()