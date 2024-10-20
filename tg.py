import asyncio
from requests_html import AsyncHTMLSession

# Define an async function to scrape a webpage
async def scrape_page(url):
    # Create an instance of AsyncHTMLSession
    session = AsyncHTMLSession()
    try:
        # Send a GET request to the URL asynchronously
        response = await session.get(url)

        # Optionally, you can render JavaScript content using response.html.arender()
        # await response.html.arender()

        # Extract data from the page (e.g., the title)
        title = response.html.find('title', first=True).text
        print(f"Title of {url}: {title}")
    except:
        print(f"Error scraping {url}")
    finally:
        # Close the session to free resources
        await session.close()

# Define the main async function to scrape multiple pages
async def main():

    
    # Create tasks for each URL to scrape them asynchronously
    tasks = [scrape_page("https://pokenea.com/") for url in range(1000)] 

    # Run the tasks concurrently
    await asyncio.gather(*tasks)

# Run the main async function
while True:
    asyncio.run(main())