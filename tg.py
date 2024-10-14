from requests_html import HTMLSession


html = HTMLSession().get("https://www.vesselfinder.com/vessels/details/503000101").html

print(html.text)