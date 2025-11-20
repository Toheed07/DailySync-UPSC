import requests
from bs4 import BeautifulSoup
import os


def get_project_root():
    """Get the project root directory (where main.py is located)."""
    current_file = os.path.abspath(__file__)
    # Go up from scrap/scrap.py to project root
    project_root = os.path.dirname(os.path.dirname(current_file))
    return project_root


def get_data_dir():
    """Get the absolute path to the data directory."""
    project_root = get_project_root()
    data_dir = os.path.join(project_root, "data")
    return data_dir


website_urls = {
    "drishti": "https://www.drishtiias.com/current-affairs-news-analysis-editorials/news-analysis/",
    "indianexpress": "https://indianexpress.com/about/current-affairs/",
}

def scrape_article(url: str, output_file: str):
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print(f"Error fetching URL: {e}")
        return

    soup = BeautifulSoup(resp.text, "html.parser")

    # Extract Title
    title = None
    title_selectors = [
        soup.find("h1"),
        soup.find("h1", class_="entry-title"),
        soup.find("h1", class_="post-title"),
        soup.find("div", class_="entry-title"),
    ]
    for selector in title_selectors:
        if selector:
            title = selector.get_text(strip=True)
            break

    # Extract Meta Line (Date + min read)
    meta_line = None
    meta_div = soup.find(lambda tag: tag.name == "div" and "min read" in tag.get_text())
    if meta_div:
        meta_line = meta_div.get_text(strip=True)

    # Extract Content
    content = ""
    content_selectors = [
        soup.find("div", class_="entry-content"),
        soup.find("div", class_="post-content"),
        soup.find("div", class_="article-content"),
        soup.find("article"),
        soup.find("div", class_="content"),
        soup.find("div", id="content"),
    ]

    content_elements = []
    content_container = None

    for selector in content_selectors:
        if selector:
            content_container = selector
            break

    if not content_container:
        content_container = soup.find("body")

    if content_container:
        for element in content_container.find_all(
            ["p", "ul", "ol", "h2", "h3", "h4", "h5", "h6"],
            recursive=True
        ):
            if element.name in ["ul", "ol"]:
                list_items = []
                for li in element.find_all("li", recursive=False):
                    text = li.get_text(strip=True)
                    if text:
                        list_items.append(f"• {text}")
                if list_items:
                    content_elements.append("\n".join(list_items))

            elif element.name in ["h2", "h3", "h4", "h5", "h6"]:
                text = element.get_text(strip=True)
                if text:
                    content_elements.append(f"\n{text}\n")

            elif element.name == "p":
                text = element.get_text(strip=True)
                if text and len(text) > 20:
                    content_elements.append(text)

    content = "\n\n".join(content_elements)

    # Write to output file
    try:
        data_dir = get_data_dir()
        os.makedirs(data_dir, exist_ok=True)
        output_file_path = os.path.join(data_dir, output_file)
        # Normalize the path to handle any issues
        output_file_path = os.path.normpath(output_file_path)
        
        with open(output_file_path, "w", encoding="utf-8") as f:
            if title:
                f.write(title + "\n")
            if meta_line:
                f.write(meta_line + "\n")
            if content:
                f.write("\n" + content)
            else:
                f.write("No content found")
    except Exception as e:
        print(f"Error writing file: {e}")
        return None

    print(f"Content saved to: {output_file_path}")
    print(f"Title: {title}")
    print(f"Content length: {len(content)} characters")

    return output_file_path


def scrape_all_articles(date: str):
    articles = []
    for website, url in website_urls.items():
        output_file = scrape_article(url=url + date, output_file=f"{date}_{website}.txt")
        
        # Check if scrape_article returned a valid file path
        if output_file is None:
            print(f"Warning: Failed to scrape {website} for date {date}")
            continue
        
        # Check if file exists before trying to read it
        if not os.path.exists(output_file):
            print(f"Warning: File not found: {output_file}")
            continue
        
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                content = f.read()
            articles.append(content)
        except Exception as e:
            print(f"Error reading file {output_file}: {e}")
            continue
        # os.remove(output_file)

    if not articles:
        raise Exception(f"No articles were successfully scraped for date {date}")
    
    final_content = "\n".join(articles)
    return final_content


# scrape_article(
#     url="https://indianexpress.com/about/current-affairs/",
#     output_file="indianexpress.txt"
# )
# scrape_article(
#     url="https://www.drishtiias.com/current-affairs-news-analysis-editorials/news-analysis/19-11-2025",
#     output_file="14ssontent.txt"
# )
# scrape_all_articles(date="19-11-2025")