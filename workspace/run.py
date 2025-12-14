#!/usr/bin/env python3
"""Run the arXiv CS Daily Flask application."""

from app import app

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)