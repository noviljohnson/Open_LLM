
from flask import Flask, request, jsonify
import ollama
from groq import Groq
import json


from configparser import ConfigParser

config_object = ConfigParser()
#Read config file
config_object.read(r"E:\Workplans\scripts\keyconfig.config")
groq_keys = config_object["Groq"]


with open(r"E:\Workplans\scripts\example_ex10.json", 'r') as fp:
    example_json = json.loads(fp.read())

with open(r"E:\Workplans\scripts\example_ex10.md", 'r') as fp:
    example_table = fp.read()

system_prompt = f"""You are an AI assistant that helps users analyze images. You will be provided with an image from a University budget allocation and expenditure document.
the following markdown table data is an example to how to interpret the given image.
Example Table : {example_table}

the Following is the expected example JSON output.
Example Json output: {example_json}

So, please understand the user provided image and return the JSON structure for the provided image.
"""

app = Flask(__name__)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    chat_history = data.get('chat_history', [])

    # Construct the full conversation prompt
    full_prompt = ""
    for entry in chat_history:
        full_prompt += f"User: {entry['user']}\n"
        full_prompt += f"Assistant: {entry['response']}\n"

    # Add the current user input
    current_input = data.get('prompt', '')
    full_prompt += f"User: {current_input}\nAssistant:"

    model=data.get("model", "llama3:latest")

    if model == "llama3.2-vision:latest":
        try:
            response = ollama.chat(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": full_prompt,
                        "images": data.get('images')
                    }
                ]
            )
            result = response['message']['content'].strip()
        except Exception as e:
            print(e)
            result = "Something went wrong! "
        
    elif model == "groq_vision":

        client = Groq(api_key=groq_keys["groq_key"])
        completion = client.chat.completions.create(
            model="llama-3.2-90b-vision-preview",
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": system_prompt + "\n\n" + full_prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                    "url": f"data:image/jpeg;base64,{data.get('images')[0]}"
                                }
                        }
                    ]
                }
            ],
            temperature=1,
            max_completion_tokens=7900,
            top_p=1,
            stream=False,
            stop=None,
        )

        result = completion.choices[0].message.content
        # ChatCompletionMessage(content='Hello, how can I assist you today?', role='assistant', function_call=None, reasoning=None, tool_calls=None)

        return jsonify({'response': result})

    else:
        # Use the ollama Python package to generate a response
        try:
            response = ollama.chat(
                model=data.get("model", "llama3:latest "),
                messages=[{'role': 'user', 'content': full_prompt}]
            )
            # Extract the model's response
            result = response['message']['content'].strip()
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return jsonify({
        'response': result
    })



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
