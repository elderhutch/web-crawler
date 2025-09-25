import sys
from crawl import *

def main():
    if len(sys.argv) < 2:
        print("no website provided")
        sys.exit(1)
    if len(sys.argv) > 2:
        print("too many arguments provided")
        sys.exit(1)
    if len(sys.argv) == 2:
        print("Script name:", sys.argv[0]) # example.py
        print("Argument:", sys.argv[1])    # -v
        print(f"starting crawl of: {sys.argv[1]} ")
        crawl_page(sys.argv[1])
        sys.exit(0)

if __name__ == "__main__":
    main()
