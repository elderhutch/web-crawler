import asyncio
import aiohttp

class AsyncCrawler:
    def __init__(self):
        base_url = ""
        base_domain = ""
        lock = asyncio.Lock()
        max_concurrency = 10
        semaphore = asyncio.Semaphore(max_concurrency)
        session = aiohttp.ClientSession()
    

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
	    await self.session.close()
          
    async def add_page_visit(self, normalized_url):
         async with self.lock:
              if self.page_data[normalized_url] in self.page_data:
                   return False
              else:
                   return True