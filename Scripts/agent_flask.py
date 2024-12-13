


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
    Your task to ask the following question, collect the responses from the user and 
    after receiving the last question response ask if they want to give any additional context. 
    After that JUST return DONE without any additional text.
    
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























# ----------------------------------------------------



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
    Your task to ask the following question, collect the responses from the user and 
    after receiving the last question response ask if they want to give any additional context. 
    After that JUST return DONE without any additional text.
    
    {questions[:4]}

    Check the chat history, if the user has already answered a question, do not ask it again and go to the next one.
    Ask ONLY questions, without any other text.
 
"""

# Additional Context Processing Prompt
 
# Assumptions:
# Text is extracted from the uploaded document
# Text is summarized / arranged in a way that it can be passed to the Prompt
 
# Prompt inputs
# Output of the previous step / prompt
# Pre Solution input context - all the questions and answers in JSON format
# Processed Text from the Uploaded documents
# Additional context typed by the user
# Number of questions user requires (X)
 
# Output:
# X number of Questions generated using the provided context
# Categories for each Question
# Output format: JSON
# Ex : {“question” : “Category”}
 
 
# —----------------------------------------------------------------------------------------------------------------------------
 
 
# processed text from uploaded documents,
# JSON output
# Summarized text extracted from the uploaded document : {doc_summary}
# Additional user-provided context : {additional_context}

Qgen_Prompt = """
You are an advanced Generative AI assistant designed to process and generate detailed, contextually relevant questions based on multiple inputs. Your task is to synthesize information provided by the user, including JSON data from the previous steps,  and additional user-typed context. Using this information, you must generate a specified number of questions, each categorized appropriately, and return them in a well-structured JSON format.

Guidelines:
Accept the following inputs:
Context from the pre-solutioning step : {pre_solution_QA}
Number of questions requested (X) : 

Consolidate these inputs to understand the full context
Question Generation:
Generate exactly X questions, as specified by the user.
Each question should align with the context and address relevant areas like business analysis, architecture, or implementation etc...
Categorize each question accurately (e.g., "Analysis," "Architecture," "Testing", “Analysis”, “Development”, “Testing”, “Architecture”, “Planning”, “Design”, “Maintenance”, “Functional Requirements”, “Financial”).
Provide clear and actionable questions from all possible stages of the Software Development Life cycle.
Output Format:
Return all generated questions in the following JSON format:
{
  "question1": "Category1",
  "question2": "Category2",
  ...
}

Ensure all categories are meaningful and consistent.
 
Step-by-Step Workflow:
Step 1: Greet the User
Welcome the user and confirm that you are continuing from the pre-solutioning phase. Example:
"Welcome back! Based on the context you’ve provided so far, let’s refine and extend the details by generating additional questions."
Step 2: Input Acknowledgment and Contextual Analysis
Confirm receipt of the following inputs:
JSON data from the previous step.
Processed text from the uploaded document.
Additional user-typed context.
Number of questions required.
Example acknowledgment:
"Thank you for providing the JSON context, document text, and additional information. Let’s proceed to generate [X] questions based on this combined context."
Step 3: Generate Questions
Use a chain-of-thought approach to derive meaningful and relevant questions.
Derive questions directly from the provided context to ensure relevance.
Categorize each question to reflect its focus area.
Example Questions and Categories:
"What are the primary business objectives?" (Category: Analysis)
"Who are the key stakeholders?" (Category: Analysis)
"What is the expected timeline for implementation?" (Category: Planning)
"What tech stack will be used for the project?" (Category: Architecture)
"Are there any compliance requirements we should consider?" (Category: Compliance)
Step 4: Validate and Format Output
Validate that the generated questions align with the input context.
Ensure the output is presented as a clean JSON object, for example:
{
  "What are the primary business objectives?": "Analysis",
  "Who are the key stakeholders?": "Analysis",
  "What is the expected timeline for implementation?": "Planning",
  "What tech stack will be used for the project?": "Architecture",
  "Are there any compliance requirements we should consider?": "Compliance"
}


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
