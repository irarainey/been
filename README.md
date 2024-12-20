# Been 🗺️

Been is a tool that creates a travel journal from photographs taken at places you have visited. The tool uses the EXIF data from the photographs, Azure Maps to reverse geocode the location, and Azure OpenAI to generate a summary of each photograph and then the journey as a whole. These summaries and image captions, together with the images and map links are combined into a markdown file to create a travel journal. Additional context also can be supplied in the form of a context file to provide further information about your trips.

An example of the output of the tool can be seen in the [example summary](/trips/summary.md) file in the trips directory within this project.

## Generating a travel summary

This project contains a devcontainer with all the required dependencies to run the tool. Clone this repository locally, and open in Visual Studio Code. You will be prompted to open the project in a devcontainer, which will install all the required dependencies, and run `poetry install` to install the required Python packages. Once open switch to the Python virtual environment using `poetry shell`.

To run the tool you first need to copy and rename the `.env.sample` file to `.env` and populate the values with your own Azure Maps and Azure OpenAI credentials. This tool requires a `gpt-4o` model to perform the image analysis.

```bash
AZURE_MAPS_KEY=<Azure Maps key>
AZURE_OPENAI_ENDPOINT=<Base URL for the OpenAI API>
AZURE_OPENAI_API_KEY=<OpenAI API key>
```

Once these values have been populated you can run the tool with the `been.sh` script from the root of the project. You will need to specify the path to the folder containing the images you wish to summarise. The tool will then create a summary of the journey using the images in the folder. The file with the summary will be saved in the output directory. If no path is supplied the default path of `./trips` will be used, as defined within this project.

If you wish to add additional context to the summary you can create a `context.txt` file in the folder containing the images. This file will be included as additional context to generate the summary, allowing for some personalisation.

```bash
./been.sh /path/to/folder
```

> ***NOTE:** Images without EXIF GPS or date time data will be ignored by the tool. If you have images you wish to include, the EXIF data can be edited to add the missing values. This can be performed using a tool such as [GeoSetter](https://geosetter.de/en/main-en/) or [ExifToolGui](https://github.com/FrankBijnen/ExifToolGui/).*