import sys
import asyncio
from crawl import *
from crawl_class import *

async def main():
    if len(sys.argv) < 4:
        print("not enough arguments provided")
        sys.exit(1)
    if len(sys.argv) > 4:
        print("too many arguments provided")
        sys.exit(1)
    if len(sys.argv) == 4:
        print("Script name:", sys.argv[0])
        print("Argument:", sys.argv[1])
        print(f"starting crawl of: {sys.argv[1]}")
        print(f"Max concurrency: {sys.argv[2]}")
        print(f"Max pages to crawl: {sys.argv[3]}")
        max_concurrency = int(sys.argv[2])
        max_pages = int(sys.argv[3])
        result = await crawl_site_async(sys.argv[1], max_concurrency, max_pages)
        print(result)
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())
