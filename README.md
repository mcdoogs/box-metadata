# box-metadata
Simple Python tool to ingest a CSV file with Box URL's and fill a column of metadata, using the Box API, for each. 



## System Setup and Requirements
Running this tool with Python 3.8+ from a Virtual Environment is recommended. Pip is recommended to install dependencies.

1. Make sure Python 3 is installed by either running `python --version` and verifying that `python` exists and refers to a 3.x installation, or try `python3 --version`, and if that works remember to use `python3` in place of just `python` for the remainder of these steps.
1. Make sure that pip is installed by running `pip --version` or `pip3 --version`, then use that command for the rest of these steps.
1. Clone this repository or download the files and extract them. 
1. Open a terminal to the root directory of this project - e.g. `cd box-metadata`
1. Create a new Python virtual environment by running `python -m venv .venv`, then make this terminal use the new virtual environment by running `source .venv/bin/activate`.
    - Any time you want to run this script from a new terminal instance, you will need to re-run the `source .venv/bin/activate` command again.
1. Now you can install the requirements into your new virtual environment by running `pip install -r requirements.txt`
    - This tool uses the [official Box Python SDK](https://github.com/box/box-python-sdk) with the extra JWT dependencies. It also uses [python-dotenv](https://github.com/theskumar/python-dotenv) to handle configuration.
1. Now your system is ready to run the script - we just have to configure the project to access your Box instance and pull the correct file metadata.

## Source CSV Structure
The source CSV should have headers with a unique name for the URL column and for the empty column of metadata to be filled in. This empty metadata column's name must match the name of the metadata you're trying to pull.

The rest of the CSV should contain one file to be processed per line. The URL should be in the `*.box.com/file/12345` format, not the 'shared link' format. If any data is already present in the column for metadata to be pulled, it will be replaced. Any other columns will be untouched and you can have as much extra data as you want. This way, if you have more than one piece of metadata to fill in, you could run this script multiple times with a new column/configuration for metadata each time. This script could also be easily expanded to pull other file attributes.

> Note: The source CSV file will not be altered by the script; instead a new CSV named 'processed.csv' will be saved to the same directory.

Example input structure, where 'someText' is the name of the metadata we want to fill out:

| someText | url | extra column |
| ----------- | ----------- | ----------- |
| | https://app.box.com/file/111222333444 | some file info to preserve
| | https://app.box.com/file/098765432100 | extra data



## Box App Creation and Authentication
We have to create an app in Box, authorize it to access the Enterprise instance we're pulling data from, and download a JSON file to authenticate with.

1. Go to the [Box Developer Console](https://app.box.com/developers/console)
1. Click on 'Create New App'
1. Select 'Custom App', leave the authentication option on '*Server Authentication (with JWT)*', and give it a descriptive name.
1. After the app is created, make sure you are on the 'Configuration' tab and scroll down to the 'Add and Manage Public Keys' section. Click on 'Generate a Public/Private Keypair' and download the JSON file to this project's directory.
1. Go over to the 'Authorization' tab and click 'Review and Submit'. 
1. This will send an email to the Enterprise administrator, who can log in and approve the request to add this application to the enterprise.
1. This application will create a new Box user in that Enterprise account. **You need to give this new system user permission to view the files the script will process by inviting its system-generated email address to become a collaborator on the appropriate folder/files in Box.** This email address will look something like `AutomationUser_12345_ABCDE@boxdevedition.com`. The easiest way to get this email address is to run the script once after completing the configuration steps below; if it encounters an error accessing a file it will output the email address to invite.

## Script Configuration
All the settings for running the script should be saved in a file named `.env` in the root directory of the project. Create a new `.env` file easily by copying the `.env.example` file (e.g. `cp .env.example .env`) and changing its contents. The parameters are as follows:
- **JWT_FILE**
    - This is the name of the JSON web token file we downloaded to authorize our app with. It's easiest if this is in the same directory as the script, but you could also use a relative path.
    - *Example:* '123456789_r22sample_config.json'
- **CSV_INPUT**
    - This is the name of the CSV file we are going to read from. See the **Source CSV Structure** section above for details on what this file should contain.
    - *Example:* 'input.csv'
- **METADATA_NAME**
    - This is the name of the piece of metadata that we want to pull from Box. This **must** match the name of the column we are going to fill out in the CSV.
    - **Important**: Box tweaks the metadata names to remove spaces, change capitalization to camelCase (for example from 'some text' to 'someText'), and seems to sometimes make arbitrary changes; you may have to run the script once to see the correct value to use here. The script will output each instance of metadata it finds on the files you've provided. Built-in metadata fields seem to be prefixed with a `$`. 
    - *Example:* 'someText'
- **URL_COLUMN**
    - This is the name of the column that contains the URL of the files to be processed.
    - *Example:* 'urls'
- **SLEEP_TIME**
    - This is how much time to wait, in seconds, between processing each file. If you find yourself running into rate limiting issues, try increasing this.
    - *Example:* 0.5

## Running the script
Basic checklist before running:
- Is the Box application created and its `.json` JWT file in this directory?
- Is a CSV with the correct file structure / column names present in this directory?
- Has the Box application been authorized by the Enterprise admins?
- Has the Box application's email address been invited as a collaborator to the files it needs to view? (Ignore if this is your first run to retrieve that email address)
- Am I in this project's virtual environment (remember to run `source .venv/bin/activate`) and have I installed the dependencies into that virtual environment using `pip`?
- Have I created an `.env` file and filled in the file names and column names?

If so, running `python main.py` should start the process; it will print its progress to the terminal and save a new CSV called `processed.csv` to this directory.