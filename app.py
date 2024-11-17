from flask import Flask, render_template
from pymongo import MongoClient
import json

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

# Fetch links from MongoDB
@app.route('/')
def display_links():
    links = []
    
    # Fetch all documents from the MongoDB collection
    documents = collection.find()

    for doc in documents:
        file_name = doc.get("file_name", "Unknown")
        document_id = str(doc.get("_id"))
        file_size = doc.get("file_size", "Unknown")
        url = f"https://filetolinkbyarctix.arctixapis.workers.dev/watch/{document_id}"
        
        # Append data to the links list
        links.append({
            "name": file_name,
            "url": url,
            "size": file_size
        })

    return render_template('links.html', links=links)

if __name__ == "__main__":
    app.run(debug=True)
    
