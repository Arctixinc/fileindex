from flask import Flask, render_template, request
from pymongo import MongoClient

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient("mongodb+srv://sibuna123:sibuna123@personalproject.rb8q7.mongodb.net")
db = client["FileStream"]
collection = db["file"]

# Pagination function
def get_paginated_links(page, per_page):
    skip = (page - 1) * per_page
    documents = collection.find().skip(skip).limit(per_page)
    links = []
    for doc in documents:
        file_name = doc.get("file_name", "Unknown")
        document_id = str(doc.get("_id"))
        file_size = doc.get("file_size", "Unknown")
        url = f"https://filetolinkbyarctix.arctixapis.workers.dev/watch/{document_id}"
        links.append({
            "name": file_name,
            "url": url,
            "size": file_size
        })
    return links

@app.route('/')
def display_links():
    page = int(request.args.get('page', 1))  # Default to page 1
    per_page = 10  # Number of links per page
    links = get_paginated_links(page, per_page)
    total_documents = collection.count_documents({})
    total_pages = (total_documents + per_page - 1) // per_page
    return render_template('links.html', links=links, page=page, total_pages=total_pages)

if __name__ == "__main__":
    app.run(debug=True, port=8080)
  
