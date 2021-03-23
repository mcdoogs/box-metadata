# box-metadata
Simple Python tool to ingest a file with Box links and fill in columns of metadata for each.

## Setup and Requirements
Running this tool with Python 3.8+ from a Virtual Environment is recommended.

This tool uses the [official Box Python SDK](https://github.com/box/box-python-sdk) with the extra JWT dependencies. It also uses [python-dotenv](https://github.com/theskumar/python-dotenv) to handle configuration.

You'll need to create an enterprise user with JWT authentication, authorize it in Box, and download the JSON config file.