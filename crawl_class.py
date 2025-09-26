import asyncio
import aiohttp
from crawl import normalize_url, extract_page_data

class AsyncCrawler:
    def __init__(self, max_concurrency=1, max_pages=3):
        self.base_url = ""
        self.base_domain = ""
        self.page_data = {}
        self.lock = asyncio.Lock()
        self.max_concurrency =   max_concurrency
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.session = None  
        self.max_pages = max_pages
        self.should_stop = False
        self.all_tasks = set()
    

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
          
    async def add_page_visit(self, normalized_url):
        if self.should_stop:
            return False
        if len(self.page_data) >= self.max_pages:
            self.should_stop = True
            print(f"Reached maximum number of pages to crawl: {self.max_pages}.")
            for task in self.all_tasks:
                task.cancel() 
            return False
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
        
    def remove_done_task(self, task):
        """Callback to remove completed tasks from the all_tasks set"""
        self.all_tasks.discard(task)

    async def crawl_page(self, base_url, current_url=None):
        try:
            if self.should_stop:
                return

            print(f"\n=== Starting crawl of page ===")
            if current_url is None:
                current_url = base_url
                print(f"No current_url provided, using base_url: {base_url}")

            normalized_url = normalize_url(current_url)
            print(f"Normalized URL: {normalized_url}")
            
            if not await self.add_page_visit(normalized_url):
                print(f"Already visited or max pages reached: {normalized_url}, skipping")
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
            
                if self.should_stop:
                    return

                print(f"\nFound {len(data['outgoing_links'])} outgoing links")
                local_tasks = set()
                for link in data["outgoing_links"]:
                    if self.should_stop:
                        break
                    normalized_link = normalize_url(link)
                    if normalized_link.startswith(normalize_url(base_url)):
                        print(f"Creating task for link: {link}")
                        task = asyncio.create_task(self.crawl_page(base_url, link))
                        task.add_done_callback(self.remove_done_task)
                        local_tasks.add(task)
                        self.all_tasks.add(task)
                    else:
                        print(f"Skipping external link: {link}")

                if local_tasks and not self.should_stop:
                    print(f"\nGathering {len(local_tasks)} tasks for this page...")
                    await asyncio.gather(*local_tasks, return_exceptions=True)
                    print("All tasks completed for this page")

        except asyncio.CancelledError:
            print(f"Crawl cancelled for {current_url}")
            raise
        except Exception as e:
            print(f"Error crawling {current_url}: {e}")
            raise
    
    async def crawl(self, base_url):
        print(f"\n=== Starting crawl of site: {base_url} ===")
        self.page_data = {}
        await self.crawl_page(base_url)
        print(f"\n=== Crawl completed. Visited {len(self.page_data)} pages ===")
        return self.page_data
    
async def crawl_site_async(base_url, max_concurrency, max_pages):
    print(f"\n=== Initializing crawler for: {base_url} ===")
    async with AsyncCrawler(max_concurrency=max_concurrency, max_pages=max_pages) as crawler:
        return await crawler.crawl(base_url)