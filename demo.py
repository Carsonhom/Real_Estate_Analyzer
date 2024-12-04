# This Python program uses HTTPS requests and OpenAI tools to create a GPT assistant to answer questions about a property.
#
# First it takes as input a US based residential address
# Then, it retrieves the property information using a HTTPS request to Zillow.com
# Then, it uploads the json response to OpenAI API
# Next, it creates a GPT assistant that references that document
# Then it creates a thread
# Then it starts a loop asking the user for questions.  When a question is entered,
# It creates a message with the question, adds it to the thread, and runs the assistant on the thread
# Finally, it displays the response from ChatGPT and starts the loop again

# Input: a user-entered residential address, and user-entered questions
# Output: displays responses to the questions about the property
import pyzill
import requests
import json
import os
import openai
from openai import OpenAI
import time # used in function to periodically check assistant status

import configparser

def create_config():
    config = configparser.ConfigParser()

    # Add sections and key-value pairs
    config['Proxy'] = {'proxy_domain': '', 'proxy_port': '', 'proxy_username': '', 'proxy_password': ''}

    # Write the configuration to a file
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

# reads property address from user input
def get_address():
    def get_non_empty_input(prompt): # Helper function to ensure input is not empty.
        while True:
            user_input = input(prompt).strip()
            if user_input:  # Ensure the input is not empty
                return user_input
            else:
                print("Input cannot be empty. Please try again.")

    # Collect and validate address components
    address_line_1 = get_non_empty_input("Enter the street address: ")
    address_city = get_non_empty_input("Enter the city: ")
    address_state = get_non_empty_input("Enter the state: ")
    address_zip = get_non_empty_input("Enter the zip code: ")

    # Combine into a full address
    property_address = f"{address_line_1}, {address_city}, {address_state}, {address_zip}"
    return property_address


# Zpid is required to make https request to zillow.com
def get_zpid():
    def get_non_empty_input(prompt): # Helper function to ensure input is not empty.
        while True:
            user_input = input(prompt).strip()
            if user_input:  # Ensure the input is not empty
                return user_input
            else:
                print("Input cannot be empty. Please try again.")
    address_zpid = get_non_empty_input("Enter the properties zpid from zillow.com: ")
    return address_zpid


# lookup information about property
def get_details(property_address, zpid):

    # Create a ConfigParser object
    config = configparser.ConfigParser()

    # Read the configuration file
    config.read('config.ini')

    # Access values from the configuration file
    proxy_domain = config.get('Proxy', 'proxy_domain')
    proxy_port = config.get('Proxy', 'proxy_port')
    proxy_username = config.get('Proxy', 'proxy_username')
    proxy_password = config.get('Proxy', 'proxy_password')

    # Return a dictionary with the retrieved values
    config_values = {
        'proxy_domain': proxy_domain,
        'proxy_port': proxy_port,
        'proxy_username': proxy_username,
        'proxy_password': proxy_password,
    }

    proxy_url = pyzill.parse_proxy(config_values['proxy_domain'],config_values['proxy_port'],config_values['proxy_username'],config_values['proxy_password']) # Residential proxy domain information
    property_url = "https://www.zillow.com/homedetails/" + property_address.replace(" ", "-").replace(",", "")  + "/" + zpid + "_zpid/" # Format url
    # sample url: "https://www.zillow.com/homedetails/858-Shady-Grove-Ln-Harrah-OK-73045/339897685_zpid/"
    # print(property_url)
    data = pyzill.get_from_home_url(property_url, proxy_url) # HTTPS request to retrieve information from zillow

    try: 
        if not data:
            raise ValueError("Data is empty. Property address is not correct.")

        jsondata = json.dumps(data, indent = 4) # Store property information in details.json

        with open("details.json", "w") as f:
            f.write(jsondata)
        print("Property data successfully retrieved 'details.json'")
    except ValueError as ve:
        print(f"ValueError: {ve}")
    except json.JSONDecodeError as je:
        print(f"JSONDecodeError: {je}")
    except IOError as ioe:
        print(f"IOError: {ioe}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


client = OpenAI(
    api_key = os.environ.get("OPENAI_API_KEY"),
)


def upload_file(path):  # Upload a file to OpenAI with an "assistants" purpose
    file = client.files.create( file=open(path, "rb"), purpose="assistants")
    # print(file)
    # print(file.id)
    return file


def create_assistant(file): # Create an assistant with OpenAI with instructions and a file to reference
    assistant = client.beta.assistants.create( 
    name="Real estate Analyzer", 
    instructions="You are a helpful and highly skilled AI assistant trained in language comprehension and summarization. Be sure not to mention if there is any issues with reading the file. Answer questions about the json file provided:", 
    model="gpt-4-turbo-preview", 
    tools=[{"type": "code_interpreter"}],
    tool_resources={ "code_interpreter": { "file_ids": [file.id] } }
    )
    return assistant

def run_assistant(message_body): # Create a message, run the assistant on it, monitor it for completion, and display the output
    # Create a message in an existing thread
    message = client.beta.threads.messages.create(
        thread_id = thread.id,
        role="user",
        content=message_body,
    )

    # Run the existing assistant on the existing thread
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )

    # Monitor the assistant and report status
    while run.status != "completed":
        run = openai.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        print(run.status)
        time.sleep(2)

    # Extract the messages from the thread
    messages = client.beta.threads.messages.list(
        thread_id=thread.id
    )

    # Display the output
    print("\nOutput:")
    for message in reversed(messages.data):
        print(message.role + ": " + message.content[0].text.value)

    return messages

if __name__ == '__main__':

    # create_config()

    print("What is the address of the property? \n")

    ######## If you do not have a proxy domain setup, comment out the commands below
    address = get_address()
    zpid = get_zpid()
    get_details(address, zpid)
    ########

    filepath = os.path.abspath('details.json')

    file = upload_file(filepath)
    assistant = create_assistant(file)

    thread = client.beta.threads.create() # Create a new thread

    # As the user for input and run the assistant on it. Loop until the user types 'exit'
    while True:
        user_input = input("Enter a question, or type 'exit' to end: ").strip().lower()
        if user_input == 'exit':
            break

        else:
            run_assistant(user_input)
