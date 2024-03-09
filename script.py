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
            Given a text input, your task is to analyze it and generate a Python script capable of producing a response in JSON format. The JSON object must consist solely of static key-value pairs, explicitly avoiding lists, sets, or any form of nested collections. Follow these guidelines:

            - The Python script must directly print the response to the console in JSON format. Use a dictionary to represent the JSON object, ensuring all keys and values are statically defined within the script.
            - Do not include comments, explanations, or references to other programming languages within the Python script. The code should stand alone and be fully executable in a Python environment.
            - Ensure the script does not attempt to answer the problem directly but rather generates code that, when executed, will produce the desired JSON response.
            Adjust your Python code accordingly to adhere to these specifications, ensuring clarity and precision in the generated output.
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
                print("Found code")
                code = code[pos + 3:]
                if code.startswith("python"):
                    code = code[6:]
                    
                pos = code.rfind("```")
                if pos != -1:
                    code = code[:pos]
            print(code)
            f.write(code)

        try:
            completed_process = subprocess.run(['python3', "response.py"], capture_output=True, text=True, check=True)
            response = completed_process.stdout
            completed_process.stdout
            return json.loads(response)
        except subprocess.CalledProcessError as e:
            # Handle errors in script execution
            error = e.stderr
            print(f"Error: {error}")
            code = fix_script(problem, code, error)
