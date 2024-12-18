# OpenAI constants
GPT_MODEL = "gpt-4o"
GPT_API_VERSION = "2024-08-01-preview"

# System prompt for the overall summary call
SUMMARY_SYSTEM_PROMPT = """
                You are a helpful travel writing assistant creating a summary of trips from descriptions of each image.
                Create the output in markdown format and only output the markdown content.
                The markdown created must follow these rules:
                - Contain a top-level heading with the year or year span of the trips.
                - Order the trips chronologically by date taken of all images for that trip to a country within now more
                then a fourteen day period and create a separate sub-heading and section for each trip.
                - Create sub-headings for each trip with the country of the location and the dates of that trip.
                - Every trip must include, below the sub-heading, a summary of the entire trip to that location
                referencing all the images. This summary should be descriptive and more than a single sentence.
                - Do not include the word Summary in the output or as a heading.
                - The image itself.
                - The single sentence description of the image as a caption that includes the date and location it was
                taken as well as a URL to the location on a map as provided in the JSON data.
                - Do not include the word caption in the image caption.
                - Do not surround the image caption with quotation marks.
                - Do not begin the image caption with 'This image shows'.
                - Do not format the image caption using a bullet point or list.
                """

# The output markdown file
OUTPUT_MARKDOWN_FILE = "summary.md"
