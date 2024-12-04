Instructions to run code:

REQUIREMENTS: Python3.10 >, OpenAI api key, residential proxy domain

1. Set OPENAI_API_KEY as environment variable

export OPENAI_API_KEY="your openai api key"

2. Edit config.ini with your proxy domain information

3. Run program at command line 

python3.10 demo.py

----------------------------------------
Code Quality, Robustness and Error Handling

Code quality: I wrote the code in python so it is easily run across platform.  I have documented the code to describe the steps that are performed for debugging purposes and ease of code maintenance.  


Robustness:  I chose to use HTTP requests to gather property information over other web scraping methods in order to optimise performance of webscraping and to abide by Zillow.com's robot.txt file.  The prompt for the LLMs was very specific to avoid unnecessaryily verbose answers from being returned.  

For error handling, users are prevented from inputing blank addresses. Incorrect addresses are detected and the user is prompted to enter the valid address. Failed curl HTTP requests are detected and an error log is returned to the user. For the LLM, a progress meter is shown to inform the user that connection to OpenAI is active and the request is being processed.  I do not restrict the types of questions being asked inorder to give the user as much flexibility as desired in prompting.

Please direct any questions to carson.hom10@gmail.com
