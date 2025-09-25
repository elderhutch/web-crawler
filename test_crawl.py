import unittest
from crawl import (normalize_url, 
                   get_h1_from_html, 
                   get_first_paragraph_from_html, 
                   get_urls_from_html,
                   get_images_from_html,
                   extract_page_data)


class TestCrawl(unittest.TestCase):
    def test_normalize_url(self):
        input_url = "https://blog.boot.dev/path"
        actual = normalize_url(input_url)
        expected = "blog.boot.dev/path"
        self.assertEqual(actual, expected)
    
    def test_normalize_url_empty(self):
        input_url = ""
        actual = normalize_url(input_url)
        expected = ""
        self.assertEqual(actual, expected)

    def test_get_h1_from_html_basic(self):
        input_body = '<html><body><h1>Test Title</h1></body></html>'
        actual = get_h1_from_html(input_body)
        expected = "Test Title"
        self.assertEqual(actual, expected)
    
    def test_get_empty_h1_from_html(self):
        input_body = '''<html><body>
            <p>Outside paragraph.</p>
            <main>
                <p>Main paragraph.</p>
            </main>
        </body></html>'''
        actual = get_first_paragraph_from_html(input_body)
        expected = ""
        self.assertNotEqual(actual, expected)

    def test_get_first_paragraph_from_html_main_priority(self):
        input_body = '''<html><body>
            <p>Outside paragraph.</p>
            <main>
                <p>Main paragraph.</p>
            </main>
        </body></html>'''
        actual = get_first_paragraph_from_html(input_body)
        expected = "Main paragraph."
        self.assertEqual(actual, expected)
    
    def test_get_empty_paragraph_from_html_main_priority(self):
        input_body = '''<html><body>
            <p>Outside paragraph.</p>
            <main>
                <h1>Main heading.</h1>
            </main>
        </body></html>'''
        actual = get_first_paragraph_from_html(input_body)
        expected = ""
        self.assertEqual(actual, expected)

    def test_get_urls_from_html_absolute(self):
        input_url = "https://blog.boot.dev"
        input_body = '<html><body><a href="https://blog.boot.dev"><span>Boot.dev</span></a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://blog.boot.dev"]
        self.assertEqual(actual, expected)

    def test_get_multiple_urls_from_html_absolute(self):
        input_url = "https://blog.boot.dev"
        input_body = '<html><body><a href="https://blog.boot.dev"><span>Boot.dev</span></a> <a href="https://api.boot.dev"></a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://api.boot.dev", "https://blog.boot.dev"]
        self.assertEqual(actual, expected)

    def test_get_no_urls_from_html_absolute(self):
        input_url = "https://blog.boot.dev"
        input_body = '<html><body>Hello Boots!</body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = []
        self.assertEqual(actual, expected)
    
    def test_get_images_from_html_relative(self):
        input_url = "https://blog.boot.dev"
        input_body = '<html><body><img src="/logo.png" alt="Logo"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://blog.boot.dev/logo.png"]
        self.assertEqual(actual, expected)

    def test_get_multiple_images_from_html_relative(self):
        input_url = "https://blog.boot.dev"
        input_body = '<html><body><img src="/logo.png" alt="Logo"><img src="/logo1.png" alt="Logo1"><img src="/logo2.png" alt="Logo2"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://blog.boot.dev/logo.png", "https://blog.boot.dev/logo1.png","https://blog.boot.dev/logo2.png"]
        self.assertEqual(actual, expected)

    def test_get_no_images_from_html_relative(self):
        input_url = "https://blog.boot.dev"
        input_body = '<html><body>SALMON</body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = []
        self.assertEqual(actual, expected)

    def test_extract_page_data_basic(self):
        input_url = "https://blog.boot.dev"
        input_body = '''<html><body>
            <h1>Test Title</h1>
            <p>This is the first paragraph.</p>
            <a href="/link1">Link 1</a>
            <img src="/image1.jpg" alt="Image 1">
        </body></html>'''
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "https://blog.boot.dev",
            "h1": "Test Title",
            "first_paragraph": "This is the first paragraph.",
            "outgoing_links": ["https://blog.boot.dev/link1"],
            "image_urls": ["https://blog.boot.dev/image1.jpg"]
        }
        self.assertEqual(actual, expected)

    def test_extract_page_data_multiple_links(self):
        input_url = "https://blog.boot.dev"
        input_body = '''<html><body>
            <h1>Test Title</h1>
            <p>This is the first paragraph.</p>
            <a href="/link1">Link 1</a>
            <a href="/link2">Link 2</a>
            <img src="/image1.jpg" alt="Image 1">
        </body></html>'''
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "https://blog.boot.dev",
            "h1": "Test Title",
            "first_paragraph": "This is the first paragraph.",
            "outgoing_links": ["https://blog.boot.dev/link1", "https://blog.boot.dev/link2"],
            "image_urls": ["https://blog.boot.dev/image1.jpg"]
        }
        self.assertEqual(actual, expected)

    def test_extract_page_data_multiple_links_images(self):
        input_url = "https://blog.boot.dev"
        input_body = '''<html><body>
            <h1>Test Title</h1>
            <p>This is the first paragraph.</p>
            <a href="/link1">Link 1</a>
            <a href="/link2">Link 2</a>
            <img src="/image1.jpg" alt="Image 1">
            <img src="/image2.jpg" alt="Image 2">
        </body></html>'''
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "https://blog.boot.dev",
            "h1": "Test Title",
            "first_paragraph": "This is the first paragraph.",
            "outgoing_links": ["https://blog.boot.dev/link1", "https://blog.boot.dev/link2"],
            "image_urls": ["https://blog.boot.dev/image1.jpg", "https://blog.boot.dev/image2.jpg"]
        }
        self.assertEqual(actual, expected)

    def test_extract_page_data_multiple_links_images_paragraphs(self):
        input_url = "https://blog.boot.dev"
        input_body = '''<html><body>
            <h1>Test Title</h1>
            <p>This is the first paragraph.</p>
            <a href="/link1">Link 1</a>
            <a href="/link2">Link 2</a>
            <p>This is the second paragraph.</p>
            <img src="/image1.jpg" alt="Image 1">
            <img src="/image2.jpg" alt="Image 2">
        </body></html>'''
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "https://blog.boot.dev",
            "h1": "Test Title",
            "first_paragraph": "This is the first paragraph.",
            "outgoing_links": ["https://blog.boot.dev/link1", "https://blog.boot.dev/link2"],
            "image_urls": ["https://blog.boot.dev/image1.jpg", "https://blog.boot.dev/image2.jpg"]
        }
        self.assertEqual(actual, expected)





    


if __name__ == "__main__":
    unittest.main()