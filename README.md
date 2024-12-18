# Been 🗺️

Been is a simple tool to create a travel journal using photographs taken from places you have visited. The tool uses the EXIF data from the photographs, Azure Maps to reverse geocode the location, and Azure OpenAI to generate a summary of each photograph and the journey as a whole using the images in the folder specified. These summaries and image captions, together with the images and map links are combined into a markdown file to create a travel journal.

An example of the output of the tool can be seen in the [example summary](/trips/summary.md) file in the images directory within this project.

## Generating a travel summary

This project contains a devcontainer with all the required dependencies to run the tool. Clone this repository locally, and open in Visual Studio Code. You will be prompted to open the project in a devcontainer, which will install all the required dependencies, and run `poetry install` to install the required Python packages. Once open switch to the Python virtual environment using `poetry shell`.

To run the tool you first need to copy and rename the `.env.sample` file to `.env` and populate the values with your own Azure Maps and Azure OpenAI credentials. This tool requires a `gpt-4o` model to perform the image analysis.

```bash
AZURE_MAPS_KEY=<Azure Maps key>
AZURE_OPENAI_ENDPOINT=<Base URL for the OpenAI API>
AZURE_OPENAI_API_KEY=<OpenAI API key>
```

Once these values have been populated you can run the tool with the `been.sh` script from the root of the project. You will need to specify the path to the folder containing the images you wish to summarise. The tool will then create a summary of the journey using the images in the folder. The summary will be saved in the same folder as the images. If no path is supplied the default path of `./trips` will be used, as defined within this project.

```bash
./been.sh /path/to/folder
```

> ***NOTE:** Images without EXIF GPS or date time data will be ignored by the tool. If you have images you wish to include the EXIF data should be edited to add the missing data.*