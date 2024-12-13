


from flask import Flask, request, jsonify
from groq import Groq

app = Flask(__name__)

# Initialize the Groq client
client = Groq()

# API endpoint to ask questions
@app.route('/ask', methods=['POST'])
def ask():
    messages = request.get_json()['messages']
    response = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=messages,
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stream=False,
        stop=None,
    )
    response = response.choices[0].message.content.strip()
    return jsonify({'response': response})

# API endpoint to generate new questions
@app.route('/generate', methods=['POST'])
def generate():
    context = request.get_json()['context']
    response = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[
            {"role": "assistant", "content": "Given the context " + context + ", generate three new questions:"},
        ],
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stream=False,
        stop=None,
    )
    response = response.choices[0].message.content.strip()
    new_questions = response.split('\n')
    for i in range(len(new_questions)):
        new_questions[i] = {"role": "assistant", "content": new_questions[i]}
    return jsonify({'new_questions': new_questions})

if __name__ == '__main__':
    app.run(debug=True)



#################################################################################################################################################






from flask import Flask, request, jsonify
from groq import Groq

app = Flask(__name__)

# Initialize the Groq client
client = Groq()



questions = [
    "What are the primary business objectives?",
    "Who are the key stakeholders?",
    "What is the expected timeline for implementation?",
    "What tech stack will be used for the project?",
    "What specific features do you want in the application?",
    "Are there any existing systems that need integration?",
    "What are your security and compliance requirements?",
    "What is your preferred user interface style?",
    "How do you envision the development process? (e.g., Agile, Waterfall)",
    "What types of testing do you expect to be performed?",
    "How often do you expect updates or maintenance to occur after deployment?",
    "What support channels do you prefer for ongoing issues or enhancements?"
]
Prompt = f"""
    You are a Generative Ai assistant.
    Firest GREET the user and ask if he ready to proceed further for building application.
    Your task to ask the following question, collect the responses from the user and after receiving the last question response JUST return DONE without any additional text.
    
    {questions[:4]}

    Check the chat history, if the user has already answered a question, do not ask it again and go to the next one.
    Ask ONLY questions, without any other text.
 
"""
messages = [{"role": "user", "content": Prompt + '\n'}]


def get_llm_response(user_messages):
    """Creates a Groq client and uses it to get an LLM response."""
    client = Groq()

    completion = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=user_messages,
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stream=True,
        stop=None,
    )
    response = ''
    for chunk in completion:
        response += chunk.choices[0].delta.content or ''
    return response

# API endpoint to ask questions
@app.route('/ask', methods=['POST'])
def ask():
    global messages
    user_res = request.get_json()['messages']

    if user_res == "EMPTY":
        llm_response = get_llm_response(messages)
        messages.append({"role":"assistant", "content":llm_response})
    else:
        messages.append({"role":"user", "content":user_res})
        llm_response = get_llm_response(messages)
        messages.append({"role":"assistant", "content":llm_response})


    return jsonify({'response': llm_response})

# API endpoint to generate new questions
@app.route('/generate', methods=['POST'])
def generate():
    context = request.get_json()['context']
    response = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[
            {"role": "assistant", "content": "Given the context " + context + ", generate three new questions:"},
        ],
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stream=False,
        stop=None,
    )
    response = response.choices[0].message.content.strip()
    new_questions = response.split('\n')
    for i in range(len(new_questions)):
        new_questions[i] = {"role": "assistant", "content": new_questions[i]}
    return jsonify({'new_questions': new_questions})

if __name__ == '__main__':
    app.run(debug=True)


