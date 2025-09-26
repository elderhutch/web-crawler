import sys
import asyncio
from crawl import *
from crawl_class import *

async def main():
    if len(sys.argv) < 2:
        print("no website provided")
        sys.exit(1)
    if len(sys.argv) > 2:
        print("too many arguments provided")
        sys.exit(1)
    if len(sys.argv) == 2:
        print("Script name:", sys.argv[0])
        print("Argument:", sys.argv[1])
        print(f"starting crawl of: {sys.argv[1]} ")
        result = await crawl_site_async(sys.argv[1])
        print(result)
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())
