import os
import re
import csv
import time
from boxsdk import Client
from boxsdk import JWTAuth
from dotenv import load_dotenv

# load our .env and set variables
load_dotenv()

JSON_PATH=os.getenv("JWT_FILE")
CSV_PATH=os.getenv("CSV_INPUT")
METADATA_NAME=os.getenv("METADATA_NAME")
URL_COLUMN=os.getenv("URL_COLUMN")
SLEEP_TIME=float(os.getenv("SLEEP_TIME"))

# load our JWT auth file and create an authorized client
config = JWTAuth.from_settings_file(JSON_PATH)
client = Client(config)

# get info about the current (application/service?) user
current_user = client.user().get()

# get csv objects for our original / new file
original_csv = open(CSV_PATH, "r", encoding='utf-8-sig')
new_csv = open("processed.csv", "w")

# create a CSV reader to process input lines and a writer to write lines into new CSV
csv_reader = csv.reader(original_csv, delimiter=',')
csv_writer = csv.writer(new_csv)

# main loop - through each row of CSV
line_count = 0
for row in csv_reader:
    # the first line should contain the header names; find the columns matching our metadata name and URL
    if line_count == 0:
        fieldnames = row
        print(f'Column names are {fieldnames}')
        try:
            metadata_index = row.index(METADATA_NAME)
            url_index = row.index(URL_COLUMN)
        except ValueError:
            print(f"Can't find columns matching both {METADATA_NAME} and {URL_COLUMN} - check the CSV at {CSV_PATH}")
            exit()
        # write out headers into the new CSV
        csv_writer.writerow(row)
        line_count += 1
    else: # for all the rest of the lines besides header...
        print('-------------------------------------------')
        print(f'Processing file at {row[url_index]}')
        # grab just the ID of the file using regex - should be first set of digits *after* box.com/file/
        id_match = re.search('(?<=box.com\/file\/)\d+', row[url_index])
        if id_match: # if we found something matching an ID in the url column of this row...
            # extract the ID number using the match object's start and end indexes
            file_id = row[url_index][id_match.start():id_match.end()]
            print(f'Found File ID of {file_id} at row {line_count}')
            try: # try to retrieve a file with the extracted ID from the Box API
                my_file = client.file(file_id).get()
                print(f'File "{my_file.name}" successfully found in Box')
                # retrieve all metadata for this file and iterate through each one
                file_metadata = my_file.get_all_metadata()
                for instance in file_metadata:
                    if METADATA_NAME in instance: # if the key for this piece of metadata matches what we want...
                        print(f'Metadata {METADATA_NAME} for file ID {file_id} has value "{instance[METADATA_NAME]}"')
                        # update our row with the value of this metadata
                        row[metadata_index] = instance[METADATA_NAME]
            except:
                # if we couldn't retrieve a file with this ID, stop processing and print some help info
                # note: the Box API will return a 404 if the user for this *automation application* (*not* your personal/work account) doesn't have correct permission
                # we print out the email address of this automation user here, which can be used to invite this user to become a collaborator on the correct files/folders
                print(f'Error getting file - does this email have permission? {current_user.login}')
                print(f'Or if you got a 429 "too many requests" error, try increasing the SLEEP_TIME parameter in the .env file')
                exit()
        else: # if we can't find a matching ID, keep working through the rest of the rows but place an error message in the output CSV
            print(f"Can't determine file ID for {row[url_index]}")
            row[metadata_index] = "Error - file ID not found"
        # write out the row to the new CSV (if we didn't find matching metadata, and didn't run into an error, this will be unchanged from the input CSV)
        csv_writer.writerow(row)
        line_count += 1
        print(f'Processed {line_count} lines so far...')
    # delay a bit here to not trip Box's rate limit
    time.sleep(SLEEP_TIME)
print(f'Processed {line_count} lines total')

