from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from datetime import datetime, timezone
import json
import pytz

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient("mongodb+srv://sibuna123:sibuna123@personalproject.rb8q7.mongodb.net")
db = client["FileStream"]
collection = db["file"]

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

def format_datetime(value):
    if isinstance(value, (int, float)):
        value = datetime.fromtimestamp(value, tz=timezone.utc)
    if isinstance(value, datetime):
        ist_time = value.astimezone(pytz.timezone('Asia/Kolkata'))
        return ist_time.strftime('%Y-%m-%d %I:%M:%S %p')
    return "Unknown"


@app.route('/')
def display_links():
    # Get the search query from the URL parameter
    search_query = request.args.get('search', '').lower()

    page = int(request.args.get('page', 1))
    per_page = 20
    skip = (page - 1) * per_page

    links = []
    suggestions = []
    total_count = 0

    if search_query:
        # Main search query
        pipeline = [
            {
                "$search": {
                    "text": {
                        "query": search_query,
                        "path": "file_name",
                        "fuzzy": {"maxEdits": 2}  # Fuzzy matching
                    }
                }
            },
            {"$sort": {"_id": -1}},
            {"$skip": skip},
            {"$limit": per_page}
        ]
        documents = list(collection.aggregate(pipeline))
        total_count = len(documents)

        # If no exact matches, find suggestions
        if not documents:
            suggestion_pipeline = [
                {
                    "$search": {
                        "autocomplete": {
                            "query": search_query,
                            "path": "file_name",
                            "fuzzy": {"maxEdits": 1}  # Autocomplete suggestions
                        }
                    }
                },
                {"$limit": 5}  # Limit the number of suggestions
            ]
            suggestions = [
                doc["file_name"] for doc in collection.aggregate(suggestion_pipeline)
            ]
    else:
        # No search query, fetch default results
        documents = collection.find().sort('_id', -1).skip(skip).limit(per_page)

    for doc in documents:
        file_name = doc.get("file_name", "Unknown")
        document_id = str(doc.get("_id"))
        file_size = doc.get("file_size", "Unknown")
        upload_time = doc.get("time", "Unknown")
        formatted_time = format_datetime(upload_time)

        url = f"https://filetolinkbyarctix.arctixapis.workers.dev/watch/{document_id}"

        links.append({
            "name": file_name,
            "url": url,
            "size": format_bytes(file_size),
            "time": formatted_time
        })

    # Total pages for pagination
    total_pages = (total_count + per_page - 1) // per_page

    return render_template(
        'links.html',
        links=links,
        suggestions=suggestions,  # Pass suggestions to the template
        page=page,
        total_pages=total_pages,
        search_query=search_query
    )

if __name__ == "__main__":
    app.run(debug=True)
