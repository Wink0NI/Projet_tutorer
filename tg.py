from requests_html import HTMLSession


html = HTMLSession().get("https://www.vesselfinder.com/fr/vessels/details/503000101").html

print(html.find('td.tpc1:contains("Ship Type") + td.tpc2'))