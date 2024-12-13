


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
