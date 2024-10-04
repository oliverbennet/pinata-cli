#!/root/pinata/bin/python

"""
Pinata CLI Program by Oliver | GraphPe
Date Created : 04-10-2024
Author : Oliver Bennet | GraphPe.com
"""

# Imports
import argparse
import sys
import json
import requests
import os
from tabulate import tabulate


def create_pinata_directory(dir_name):
    """Create a directory in the user's home directory if it does not exist.

    Args:
        dir_name (str): The name of the directory to create.
    """
    # Get the user's home directory
    home_directory = os.path.expanduser("~")
    directory_path = os.path.join(home_directory, dir_name)

    try:
        # Check if the directory already exists
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
            return True
        else:
            return True
    except Exception as e:
        print(f"An error occurred while creating the directory: {e}")
        return False

def save_token_to_file(file_name, content):
    """Save a string to a file in the specified directory.

    Args:
        dir_path (str): The path of the directory to save the file in.
        file_name (str): The name of the file to create (with .txt extension).
        content (str): The string content to write to the file.
    """
    home_directory = os.path.expanduser("~")
    dir_path = os.path.join(home_directory, ".pinata")

    file_path = os.path.join(dir_path, file_name)

    try:
        with open(file_path, 'w') as file:
            file.write(content)
        return True
    except Exception as e:
        print(f"An error occurred while saving the content: {e}")
        return False


def read_token():
    """Read content from a specified file.

    Args:
        file_path (str): The path to the file to read.

    Returns:
        str: The content of the file, or an error message if the file does not exist.
    """
    home_directory = os.path.expanduser("~")
    file_path = os.path.join(home_directory, ".pinata", ".credentials")
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        return False
    except Exception as e:
        return False


def test_pinata_authentication():
    """Test authentication with the Pinata API.
    Returns:
        dict: The JSON response from the API, or an error message.
    """
    api_key = read_token()
    if not api_key:
        print("Error Reading Pinata API Token, Run Setup First using ./pinata-cli -s")
        sys.exit(1)
    url = "https://api.pinata.cloud/data/testAuthentication"
    headers = {
        'accept': 'application/json',
        'authorization': f'Bearer {api_key}',
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses (4xx and 5xx)
        print(response.json().get('message')) 
        return response.json()  # Return the JSON response if successful

    except requests.exceptions.HTTPError as http_err:
        return {"error": f"HTTP error occurred: {http_err}"}
    except Exception as err:
        return {"error": f"An error occurred: {err}"}


def upload_file_to_pinata(file_path):
    """Upload a file to the Pinata API.

    Args:
        file_path (str): The path to the file to upload.
        name (str): The name to assign to the file in Pinata.

    Returns:
        dict: The JSON response from the API, or an error message.
    """
    api_key = read_token()
    if not api_key:
        print("Error Reading Pinata API Token, Run Setup First using ./pinata-cli -s")
        sys.exit(1)

    url = "https://uploads.pinata.cloud/v3/files"
    headers = {
        'Authorization': f'Bearer {api_key}',
        #'Content-Type': 'multipart/form-data',
    }

    with open(file_path, 'rb') as file_data:
        # Define the files and data for the form
        files = {
            'file': (file_path.split('/')[-1], file_data)
        }
        data = {
            'name': file_path.split('/')[-1]
        }
        
        try:
            print("File Uploading.....")
            response = requests.post(url, headers=headers, files=files, data=data)
            response.raise_for_status()  # Raise an error for bad responses (4xx and 5xx)
            print("File Uploaded Successfully, use -l to list new files")
            return response.json()  # Return the JSON response if successful
        except requests.exceptions.HTTPError as http_err:
            print({"error": f"HTTP error occurred: {http_err}"})
        except Exception as err:
            print({"error": f"An error occurred: {err}"})
        finally:
            # Ensure the file is closed after the request
            pass


def main():
    """ Main entry point for the CLI Program """
    print("""  _____ _             _             _____ _      _____
 |  __ (_)           | |           / ____| |    |_   _|
 | |__) | _ __   __ _| |_ __ _    | |    | |      | |
 |  ___/ | '_ \\ / _` | __/ _` |   | |    | |      | |
 | |   | | | | | (_| | || (_| |   | |____| |____ _| |_
 |_|   |_|_| |_|\\__,_|\\__\\__,_|    \\_____|______|_____|
                                                       """)
    parser = argparse.ArgumentParser(description="""All in One CLI Program to Access Pinata Cloud""")

    # Define command-line arguments
    parser.add_argument('-s', '--setup', action="store_true", help='The command to setup Pinata JWT Token')
    parser.add_argument('-a', '--authtest', action="store_true", help='The command to test your Authentication with Pinata')
    parser.add_argument('-u', '--uploadfile', help='The command to upload a file from your local machine to Pinata Server')
    parser.add_argument('-l', '--listfiles', action="store_true", help='The command will list all the files stored in your Pinata Account')
    parser.add_argument('-f', '--getfile',  help='Get Single File by id, use -l to get ID of all files')
    parser.add_argument('-p', '--updatefile',  help='Update file Properties e.g id=fileid,name=newname')
    parser.add_argument('-d', '--deletefile',  help='Delete a file by ID in Pinata')

    args = parser.parse_args()

    # Call appropriate function based on command
    if args.setup:
        setup_pinata_api()
    elif args.authtest:
        test_pinata_authentication()
    elif args.uploadfile:
        upload_file_to_pinata(args.uploadfile)
    elif args.listfiles:
        get_pinata_files()
    elif args.getfile:
        get_pinata_file_details(args.getfile)
    elif args.updatefile:
        update_pinata_file(args.updatefile)
    elif args.deletefile:
        delete_pinata_file(args.deletefile)

    else:
        print("Error: Invalid Options, Use -h for detailed Help")
        sys.exit(1)


def get_pinata_files():
    """Fetch files from the Pinata API.

    Returns:
        dict: The JSON response from the API, or an error message.
    """
    api_key = read_token()
    if not api_key:
        print("Error Reading Pinata API Token, Run Setup First using ./pinata-cli -s")
        sys.exit(1)

    url = "https://api.pinata.cloud/v3/files"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses (4xx and 5xx)
        result = response.json()
        if 'data' in result and 'files' in result['data']:
            files = result['data']['files']
            #print(files)
            display_pinata_files(files)
        else:
            print("Error:", result)
        return response.json()  # Return the JSON response if successful
    except requests.exceptions.HTTPError as http_err:
        return {"error": f"HTTP error occurred: {http_err}"}
    except Exception as err:
        return {"error": f"An error occurred: {err}"}


def display_pinata_files(files_data):
    """Display Pinata file data in a tabular format.

    Args:
        files_data (list): A list of file dictionaries with file details.
    """
    # Prepare the headers
    headers = ["ID", "Name", "CID", "Group ID"]

    # Prepare the rows for the table
    table_data = [
        [file['id'], file['name'], file['cid'], file['group_id']]
        for file in files_data
    ]

    # Print the table
    print(tabulate(table_data, headers=headers, tablefmt="pretty"))
   

def get_pinata_file_details(file_id):
    """Fetch details of a specific file from Pinata API and display them in a tabular format.

    Args:
        file_id (str): The ID of the file to retrieve details for.

    Returns:
        None: Prints the file details in a table format.
    """
    api_key = read_token()
    if not api_key:
        print("Error Reading Pinata API Token, Run Setup First using ./pinata-cli -s")
        sys.exit(1)

    # Define the API endpoint with the given file ID
    url = f"https://api.pinata.cloud/v3/files/{file_id}"

    # Define headers for the request
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    try:
        # Make the GET request to the API
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)

        # Parse the response as JSON
        file_data = response.json().get('data', {})

        # Extract relevant fields for tabular display
        table_data = [
            ["ID", file_data.get("id", "N/A")],
            ["Name", file_data.get("name", "N/A")],
            ["CID", file_data.get("cid", "N/A")],
            ["Size (bytes)", file_data.get("size", "N/A")],
            ["Number of Files", file_data.get("number_of_files", "N/A")],
            ["MIME Type", file_data.get("mime_type", "N/A")],
            ["Group ID", file_data.get("group_id", "N/A")],
            ["Created At", file_data.get("created_at", "N/A")],
        ]

        # Check for keyvalues and include them if available
        keyvalues = file_data.get("keyvalues", {})
        if keyvalues:
            table_data.append(["Keyvalues", str(keyvalues)])

        # Display the data in a table format
        print(tabulate(table_data, headers=["Field", "Value"], tablefmt="pretty"))

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")


def update_pinata_file(data):
    """Update file details on Pinata by specifying the file ID, new name, and key-values.

    Args:
        file_id (str): The ID of the file to update.
        new_name (str): The new name to assign to the file.
        keyvalues (dict): Key-value pairs to update.

    Returns:
        dict: The JSON response from the API, or an error message.
    """
    file_id, new_name = data.split(",")

    file_id = file_id.split("=")[1]
    new_name = new_name.split("=")[1]

    api_key = read_token()
    if not api_key:
        print("Error Reading Pinata API Token, Run Setup First using ./pinata-cli -s")
        sys.exit(1)

    # Define the API endpoint with the file ID
    url = f"https://api.pinata.cloud/v3/files/{file_id}"
    keyvalues = {}
    # Prepare the payload with the new name and keyvalues
    payload = {
        "name": new_name,
        "keyvalues": keyvalues
    }

    # Set headers including the authorization token and content type
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        # Make the PUT request to the API
        response = requests.put(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
        print("values updated successfully, run -l to check updated values")
        # Return the JSON response if successful
        return response.json()

    except requests.exceptions.HTTPError as http_err:
        print({"error": f"HTTP error occurred: {http_err}"})
    except Exception as err:
        print({"error": f"An error occurred: {err}"})


def delete_pinata_file(file_id):
    """Delete a file on Pinata by specifying the file ID.

    Args:
        file_id (str): The ID of the file to delete.

    Returns:
        dict: The JSON response from the API, or an error message.
    """
    api_key = read_token()
    if not api_key:
        print("Error Reading Pinata API Token, Run Setup First using ./pinata-cli -s")
        sys.exit(1)


    confirms = ["y","yes"]
    user_confirmation = input(f"Are you Sure you want to Delete the file with ID [{file_id}] (Yes / No):")
    if not user_confirmation:
        print("exiting as there are no inputs, Default is NO")
        sys.exit(1)
    if not user_confirmation.lower() in confirms:
        print("User Confirmed NO")
        sys.exit(1)

    # Define the API endpoint with the file ID
    url = f"https://api.pinata.cloud/v3/files/{file_id}"
    
    # Set the authorization headers
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    try:
        # Make the DELETE request to the API
        response = requests.delete(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
        
        # Return the JSON response if successful
        print("File deleted successfully") if response.status_code == 200 else response.json()
    except requests.exceptions.HTTPError as http_err:
        print({"error": f"HTTP error occurred: {http_err}"})
    except Exception as err:
        print({"error": f"An error occurred: {err}"})


def setup_pinata_api():
    JWT = input("Enter Your Pinata JWT:")
    ret_status = create_pinata_directory(".pinata")
    if ret_status:
        save_status = save_token_to_file(".credentials",JWT)
        if save_status:
            print("Token Saved Sucessfully, You can Proceed with Other Activities")
            sys.exit(0)
        else:
            print("Error in Saving JWT Token")
            sys.exit(1)
    else:
        print("Error in Saving JWT Token")
        sys.exit(1)

if __name__ == "__main__":
    main()
