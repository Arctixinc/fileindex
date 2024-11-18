from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
import json
from datetime import datetime

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient("mongodb+srv://sibuna123:sibuna123@personalproject.rb8q7.mongodb.net")
db = client["FileStream"]  # Database name
collection = db["file"]    # Collection name

# Custom filter for size formatting
@app.template_filter('format_bytes')
def format_bytes(bytes):
    if bytes < 1024:
        return f"{bytes} B"
    elif bytes < 1048576:
        return f"{bytes / 1024:.2f} KB"
    elif bytes < 1073741824:
        return f"{bytes / 1048576:.2f} MB"
    else:
        return f"{bytes / 1073741824:.2f} GB"


@app.template_filter('format_datetime')
def format_datetime(value):
    if isinstance(value, (int, float)):
        value = datetime.fromtimestamp(value)
    return value.strftime('%Y-%m-%d %I:%M:%S %p') if isinstance(value, datetime) else "Unknown"


@app.route('/')
def display_links():
    # Get the current page number from query parameters, default to 1
    page = int(request.args.get('page', 1))
    per_page = 20  # Items per page

    # Calculate the skip value
    skip = (page - 1) * per_page

    # Fetch documents with skip and limit for pagination
    documents = collection.find().sort('_id', -1).skip(skip).limit(per_page)

    # Count total documents to calculate total pages
    total_count = collection.count_documents({})
    total_pages = (total_count + per_page - 1) // per_page

    links = []
    for doc in documents:
        file_name = doc.get("file_name", "Unknown")
        document_id = str(doc.get("_id"))
        file_size = doc.get("file_size", "Unknown")
        upload_time = doc.get("time")  # Ensure "time" field exists in your MongoDB documents
        url = f"https://filetolinkbyarctix.arctixapis.workers.dev/watch/{document_id}"
        
        links.append({
            "name": file_name,
            "url": url,
            "size": format_bytes(file_size),
            "time": format_datetime(upload_time)
        })
        

    return render_template('links.html', links=links, page=page, total_pages=total_pages)


@app.route('/status')
def status():
    return jsonify({"status": "Server is running"}), 200

if __name__ == "__main__":
    app.run(debug=True)
