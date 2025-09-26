import csv

def write_csv_report(page_data, filename="report.csv"):
    if not page_data:
        print("No data to write to CSV.")
        return
    
    fieldnames = ["page_url", "h1", "first_paragraph", "outgoing_link_urls", "image_urls"]
    
    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for data in page_data.values():
                writer.writerow({
                    "page_url": data.get("url", ""),
                    "h1": data.get("h1", ""),
                    "first_paragraph": data.get("first_paragraph", ""),
                    "outgoing_link_urls": "; ".join(data.get("outgoing_links", [])),
                    "image_urls": "; ".join(data.get("image_urls", []))
                })
        print(f"CSV report written to {filename}")
    except IOError as e:
        print(f"Error writing CSV file: {e}")