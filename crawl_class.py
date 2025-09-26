import asyncio
import aiohttp
from crawl import normalize_url, extract_page_data

class AsyncCrawler:
    def __init__(self):
        self.base_url = ""
        self.base_domain = ""
        self.page_data = {}
        self.lock = asyncio.Lock()
        max_concurrency = 3  
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.session = None  
    

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
          
    async def add_page_visit(self, normalized_url):
         async with self.lock:
              if normalized_url in self.page_data:
                   return False
              else:
                   return True
    
    async def get_html(self, url):
        try:
             # Add timeout to prevent hanging on slow requests
             timeout = aiohttp.ClientTimeout(total=10)  # 10 second timeout
             print(f"Attempting to fetch HTML for: {url}")
             async with self.session.get(url, headers={"User-Agent": "BootCrawler/1.0"}, timeout=timeout) as response:
                print(f"Got response with status {response.status} for: {url}")
                if response.status == 200:
                    html = await response.text()
                    print(f"Successfully retrieved HTML for: {url} (length: {len(html)} chars)")
                    return html
                else:
                    print(f"Error: Received status code {response.status} for URL: {url}")
                    return None
            
        except asyncio.TimeoutError:
            print(f"Timeout error while fetching URL: {url}")
            return None
        except aiohttp.ClientError as e:
            print(f"Error: An exception occurred while trying to fetch the URL: {url}\n{e}")
            return None
        
    async def crawl_page(self, base_url, current_url=None):
        print(f"\n=== Starting crawl of page ===")
        if current_url is None:
            current_url = base_url
            print(f"No current_url provided, using base_url: {base_url}")

        normalized_url = normalize_url(current_url)
        print(f"Normalized URL: {normalized_url}")
        
        if not await self.add_page_visit(normalized_url):
            print(f"Already visited {normalized_url}, skipping")
            return
            
        async with self.semaphore:
            print(f"Acquired semaphore, crawling: {current_url}")
            html = await self.get_html(current_url)
            if html is None:
                print(f"Failed to get HTML for {current_url}")
                return

            print(f"Successfully got HTML for {current_url}, extracting data...")
            data = extract_page_data(html, current_url)
            async with self.lock:
                self.page_data[normalized_url] = data
                print(f"Stored data for {normalized_url}")
        
            tasks = []
            print(f"\nFound {len(data['outgoing_links'])} outgoing links")
            for link in data["outgoing_links"]:
                normalized_link = normalize_url(link)
                if normalized_link.startswith(normalize_url(base_url)):
                    print(f"Creating task for link: {link}")
                    tasks.append(asyncio.create_task(self.crawl_page(base_url, link)))
                else:
                    print(f"Skipping external link: {link}")

            if tasks:
                print(f"\nGathering {len(tasks)} tasks...")
                await asyncio.gather(*tasks)
                print("All tasks completed for this page")
    
    async def crawl(self, base_url):
        print(f"\n=== Starting crawl of site: {base_url} ===")
        self.page_data = {}
        await self.crawl_page(base_url)
        print(f"\n=== Crawl completed. Visited {len(self.page_data)} pages ===")
        return self.page_data
    
async def crawl_site_async(base_url):
    print(f"\n=== Initializing crawler for: {base_url} ===")
    async with AsyncCrawler() as crawler:
        return await crawler.crawl(base_url)