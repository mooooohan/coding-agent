from flask import render_template, request, jsonify
from app import app
import json
import os
import time
import subprocess

# Function to load papers from JSON file and update if necessary
def load_papers():
    """Load papers from the JSON file and update if necessary"""
    papers_path = os.path.join(app.root_path, '..', app.config['PAPERS_JSON_PATH'])
    
    # Check if papers file exists
    if not os.path.exists(papers_path):
        # If file doesn't exist, fetch papers
        update_papers()
    else:
        # Check if it's time to update papers (every 24 hours)
        last_modified = os.path.getmtime(papers_path)
        current_time = time.time()
        hours_since_last_update = (current_time - last_modified) / 3600
        
        # If more than 24 hours since last update, fetch new papers
        if hours_since_last_update > 24:
            update_papers()
    
    # Load papers from JSON file
    try:
        with open(papers_path, 'r', encoding='utf-8') as f:
            papers = json.load(f)
        return papers
    except Exception as e:
        app.logger.error(f"Error loading papers: {str(e)}")
        return []

# Function to update papers by calling data_fetcher.py
def update_papers():
    """Update papers by calling data_fetcher.py"""
    try:
        data_fetcher_path = os.path.join(app.root_path, '..', 'data_fetcher.py')
        subprocess.run(['python', data_fetcher_path], check=True, capture_output=True, text=True)
        app.logger.info("Papers successfully updated")
    except Exception as e:
        app.logger.error(f"Error updating papers: {str(e)}")

# Homepage route

def index(category=None):
    """Display the homepage with all papers or filtered by category"""
    papers = load_papers()
    # Filter papers by category if specified
    if category:
        filtered_papers = []
        for paper in papers:
            paper_categories = paper.get('categories', [])
            # Handle case where categories might be a string instead of list
            if isinstance(paper_categories, str):
                paper_categories = paper_categories.split(',')
            # Filter out any None values and strip whitespace
            paper_categories = [cat.strip() for cat in paper_categories if cat is not None]
            # Check if any category matches
            if any(cat == category for cat in paper_categories):
                filtered_papers.append(paper)
        return render_template('index.html', papers=filtered_papers, categories=['cs.AI', 'cs.CV', 'cs.SE', 'cs.TH', 'cs.SY', 'cs.LG', 'cs.CL', 'cs.NE', 'cs.RO', 'cs.GT', 'cs.MM'], selected_category=category)
    return render_template('index.html', papers=papers, categories=['cs.AI', 'cs.CV', 'cs.SE', 'cs.TH', 'cs.SY', 'cs.LG', 'cs.CL', 'cs.NE', 'cs.RO', 'cs.GT', 'cs.MM'], selected_category=None)

# Detail page route
def paper_detail(paper_index):
    """Display the detail page for a specific paper"""
    papers = load_papers()
    try:
        index = int(paper_index)
        if 0 <= index < len(papers):
            paper = papers[index]
            return render_template('detail.html', paper=paper, paper_index=index, papers=papers)
        else:
            return render_template('404.html'), 404
    except ValueError:
        return render_template('404.html'), 404

# API route to get all papers
@app.route('/api/papers', methods=['GET'])
def api_papers():
    """API endpoint to get all papers"""
    papers = load_papers()
    return jsonify({'papers': papers})

# Register routes
app.add_url_rule('/', 'index', index)
app.add_url_rule('/category/<category>', 'index', index)
app.add_url_rule('/paper/<paper_index>', 'paper_detail', paper_detail)

# Error handlers
@app.errorhandler(404)
def page_not_found(error):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(error):
    """Handle 500 errors"""
    return render_template('500.html'), 500