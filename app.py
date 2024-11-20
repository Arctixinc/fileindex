from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from datetime import datetime, timezone, timedelta
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
    # Get search, sort, and filter parameters
    search_query = request.args.get('search', '').lower()
    sort_field = request.args.get('sort_field', 'time')  # Default sort by 'time'
    sort_order = request.args.get('sort_order', 'desc')  # Default to descending order
    date = request.args.get('date', '')  # Specific date (YYYY-MM-DD)
    start_date = request.args.get('start_date', '')  # Start date (YYYY-MM-DD)
    end_date = request.args.get('end_date', '')  # End date (YYYY-MM-DD)

    # Determine sorting direction
    sort_direction = -1 if sort_order == 'desc' else 1

    # Build the MongoDB query
    query = {}
    if search_query:
        query["file_name"] = {"$regex": search_query, "$options": "i"}

    # Filter by specific date
    if date:
        try:
            # Parse the specific date
            date_start = datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            date_end = date_start + timedelta(days=1)  # End of the day
            query["time"] = {"$gte": date_start.timestamp(), "$lt": date_end.timestamp()}
        except ValueError:
            pass  # Ignore invalid date formats

    # Filter by date range (start_date and end_date)
    if start_date or end_date:
        try:
            date_filter = {}
            if start_date:
                start_datetime = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                date_filter["$gte"] = start_datetime.timestamp()
            if end_date:
                end_datetime = datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=timezone.utc) + timedelta(days=1)
                date_filter["$lt"] = end_datetime.timestamp()
            query["time"] = date_filter
        except ValueError:
            pass  # Ignore invalid date formats

    # Fetch documents with search, filter, and sort query
    documents = (
        collection.find(query)
        .sort(sort_field, sort_direction)
        .skip((int(request.args.get('page', 1)) - 1) * 20)
        .limit(20)
    )

    # Count total documents
    total_count = collection.count_documents(query)
    total_pages = (total_count + 19) // 20

    # Format data for rendering
    links = []
    for doc in documents:
        links.append({
            "name": doc.get("file_name", "Unknown"),
            "url": f"https://filetolinkbyarctix.arctixapis.workers.dev/watch/{str(doc.get('_id'))}",
            "size": format_bytes(doc.get("file_size", 0)),
            "time": format_datetime(doc.get("time"))
        })

    return render_template(
        'links.html',
        links=links,
        page=int(request.args.get('page', 1)),
        total_pages=total_pages,
        search_query=search_query,
        total_count=total_count,
        sort_field=sort_field,
        sort_order=sort_order,
        date=date,
        start_date=start_date,
        end_date=end_date
    )
    


    
@app.route('/status')
def status():
    return jsonify({"status": "Server is running"}), 200


if __name__ == "__main__":
    app.run(debug=True)
