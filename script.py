import json
import subprocess
import os

from groq import Groq

client = Groq(
    api_key=os.environ["API_KEY"],
)


def fix_script(problem, script, error):
    messages = [
            {
                "role": "system",
                "content": """
                    You are a python 3 expert and you have to fix scripts.
                    The user will provide a python script and an error message.
                    You have to fix the script to make it work correctly.
                    The response is the fixed script ready to be executed without explainations.
                    May be the error is because the script contains text that is not valid python code this could be because the user has written comments or explanations in the script. So rewrite the script without comments or explanations.
                    Never use user inputs like input() in the script.
                """,
            },
            {
                "role": "user",
                "content": f"""
                    The task that has to be solved is the following:
                    {problem}
                    
                    The script that has to be fixed is the following:
                    {script}
                    
                    The error message is the following:
                    {error}
                """
            }
    ]
    
    chat_completion = client.chat.completions.create(
        messages=messages,
        model="mixtral-8x7b-32768",
    )
    
    code = chat_completion.choices[0].message.content
    
    return code

def solve(problem):
    messages = [
        {
            "role": "system",
            "content": """
Given a text input, your task is to analyze it and create a Python script that dynamically calculates and produces a response in JSON format based on the current or input data. The script should utilize appropriate Python libraries or functions to gather or compute the required information. The JSON object must be generated dynamically, reflecting the real-time or input-based data. Follow these guidelines:

- Ensure the Python script utilizes libraries or functions to dynamically compute values or responses. For instance, use the `datetime` library to fetch the current time if the question is related to time.
- The Python script must print the response to the console in JSON format. Use a dictionary to represent the JSON object, ensuring keys and values are dynamically defined within the script based on computations or data retrieval. Use the `json.dumps()` function to convert the dictionary to a JSON string.
- Exclude comments, unnecessary explanations, or references to other programming languages within the Python script. The code should be self-contained, executable in a Python environment, and directly relevant to the task.
- Focus on generating code that, when executed, dynamically produces the desired JSON response based on the actual data or computations at the moment of execution.

Adjust your Python code accordingly to adhere to these specifications, ensuring the output is dynamic, relevant, and precise.
            """,
        },
        {
            "role": "user",
            "content": problem
        }
    ]
    
    chat_completion = client.chat.completions.create(
        messages=messages,
        model="mixtral-8x7b-32768",
    )

    code = chat_completion.choices[0].message.content
    success = False

    while not success:
        if code == "NO":
            raise ValueError("No response was generated")
        # Write the code to a file
        with open("response.py", "w") as f:
            # Check contains ```python and ``` at the start and end of the code respectively and remove them
            pos = code.find("```")
            if pos != -1:
                code = code[pos + 3:]
                if code.startswith("python"):
                    code = code[6:]
                    
                pos = code.rfind("```")
                if pos != -1:
                    code = code[:pos]
            f.write(code)

        try:
            completed_process = subprocess.run(['python3', "response.py"], capture_output=True, text=True, check=True)
            response = completed_process.stdout
            completed_process.stdout
            return json.loads(response), code
        except subprocess.CalledProcessError as e:
            # Handle errors in script execution
            error = e.stderr
            print(f"Error: {error}")
            code = fix_script(problem, code, error)

def present_solution(problem, solution, code):
    if not isinstance(solution, dict):
        raise ValueError("The solution must be a dictionary")
    list_of_keys = ["{" + str(key) + "}" for key in solution.keys() ]
    list_of_keys = ", ".join(list_of_keys)    
    messages = [
        {
            "role": "system",
            "content": """
                According to the list of keys provided and the problem statement, you have to generate a response in text format that will be converted to speech by a text-to-speech system.
                So your response will not be read directly by the user but will be converted to speech.
                To insert the values of the keys in the response, use the following format: {key} for each key.
            """,
        },
        {
            "role": "user",
            "content": f"""
                The task that has to be solved is the following:
                {problem}
                

                Don't explain the code, just provide the response in text format.
                The list of keys is the following:
                {list_of_keys}
                
            """
        }
    ]
    
    chat_completion = client.chat.completions.create(
        messages=messages,
        model="mixtral-8x7b-32768",
    )
    
    response = chat_completion.choices[0].message.content
    
    for key in solution.keys():
        response = response.replace(f"{{{key}}}", str(solution[key]))
        
    return response
