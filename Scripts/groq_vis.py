from groq import Groq

client = Groq()
completion = client.chat.completions.create(
    model="llama-3.2-90b-vision-preview",
    messages=[],
    temperature=1,
    max_completion_tokens=1024,
    top_p=1,
    stream=False,
    stop=None,
)

print(completion.choices[0].message)


import json
with open(r"E:\Workplans\scripts\example_ex10.json", 'r') as fp:
    example_json = json.loads(fp.read())
example_json['Exhibit 10 - UNM MAIN Campus']
with open(r"E:\Workplans\scripts\example_ex10.md", 'r') as fp:
    example_table = fp.read()
print(example_table)
system_prompt = f"""You are an AI assistant that helps users analyze images. You will be provided with an image from a Univercity budget allocation and expenditure document.
the following markdown table data is an exmple to how to interpret the given image.
Example Table : {example_table}

the Following is the expected example JSON output.
Example Json output: {example_json}

So, please understand the user provided image and return the JSON structure for the provided image.
"""
print(system_prompt)
nSystem_prompt = f""" 
You are an AI assistant that helps user to structure the extracted data from a University budget allocation and expenditure document in MARKDOWN format.
the following markdown table data is an example to how to interpret a table in the given markdown data. 
Example Table: {example_table}

the Following is the expected example JSON output.
Example Json output: {example_json}

please understand the user provided DATA and return the JSON structure.
"""
print(nSystem_prompt)


from llama_index.llms.bedrock import Bedrock
from configparser import ConfigParser
from llama_index.core.llms import ChatMessage
import pandas as pd

config_object = ConfigParser()
#Read config file
config_object.read(r"E:\KG\DocConfig.config")
aws_info = config_object["AWS"]


## bedrock llm
model_id="anthropic.claude-3-sonnet-20240229-v1:0"
# model_id="meta.llama3-70b-instruct-v1:0"
# model_id="mistral.mixtral-8x7b-instruct-v0:1"
llm = Bedrock(
    model=model_id,
    region_name='us-east-1',
    aws_access_key_id=aws_info['aws_access_key_id'],
    aws_secret_access_key=aws_info['aws_secret_access_key']
)

markdown_data = """
## **Exhibit 10 - UNM MAIN Campus**

**Expenditures for Instruction**

| Original    | Revised     |              |
|-------------|-------------|--------------|
| Budget 2023 | Budget 2023 | Actuals 2023 |
| PERIOD 14   | PERIOD 14   | PERIOD 14    |

|                                       |                           |                                                         |             |             | Unrestricted Restricted Unrestricted Restricted |             | Unrestricted                                                          | Restricted     |
|---------------------------------------|---------------------------|---------------------------------------------------------|-------------|-------------|-------------------------------------------------|-------------|-----------------------------------------------------------------------|----------------|
| General Academic                      | School of Engineering SOE | Engineering General                                     | 481,580     | 0           | 476,994                                         | 0           | 435,376.63                                                            | .00            |
| Instruction                           |                           | Academic                                                |             |             |                                                 |             |                                                                       |                |
|                                       |                           | Mechanical Engineering                                  | 3,184,840   | 0           | 3,248,945                                       | 0           | 3,159,030.27                                                          | .00            |
|                                       | School of Law LAW         | Law                                                     | 7,117,683   | 0           | 7,189,179                                       | 0           | 6,611,420.08                                                          | .00            |
|                                       | University College UC     | AFROTC                                                  | 0           | 0           | 42,062                                          | 0           | 23,817.90                                                             | .00            |
|                                       |                           | Army ROTC                                               | 0           | 0           | 72,491                                          | 0           | 57,173.97                                                             | .00            |
|                                       |                           | NROTC                                                   | 0           | 0           | 34,893                                          | 0           | 16,916.53                                                             | .00            |
|                                       |                           | University College                                      | 661,141     | 0           | 805,862                                         | 0           | 721,870.76                                                            | .00            |
|                                       | VP Student Affairs        | AFROTC                                                  | 105,164     | 0           | 0                                               | 0           | .01                                                                   | .00            |
|                                       | Administration            |                                                         |             |             |                                                 |             |                                                                       |                |
|                                       |                           | Army ROTC                                               | 69,857      | 0           | 0                                               | 0           | .00                                                                   | .00            |
|                                       |                           | Curanderismo Class                                      | 14,810      | 0           | 0                                               | 0           | .00                                                                   | .00            |
|                                       |                           | NROTC                                                   | 71,756      | 0           | 0                                               | 0           | 31.23                                                                 | .00            |
|                                       |                           | VP for Equity and Inclusion VP for Equity and Inclusion | 258,361     | 0           | 82,361                                          | 0           | 11,158.50                                                             | .00            |
| Total General Academic Instruction    |                           |                                                         | 184,188,213 |             | 0 185,423,510                                   |             | 0 173,959,089.90                                                      | .00            |
| Off-Campus Extension                  | UNM Online                | Extended Services                                       | 60,000      | 0           | 42,347                                          | 0           | 4,557.32                                                              | .00            |
|                                       |                           | Internet Pilot Project                                  | 0           | 0           | 0                                               | 0           | 17,965.67                                                             | .00            |
| Total Off-Campus Extension            |                           |                                                         | 60,000      | 0           | 42,347                                          | 0           | 22,522.99                                                             | .00            |
| Other                                 | EVP Admin Independent     | I&G Programs                                            |             | 0 2,850,000 | 0                                               | 2,850,000   | .00                                                                   | 503,294.00     |
|                                       | Offices                   |                                                         |             |             |                                                 |             |                                                                       |                |
| Total Other                           |                           |                                                         |             | 0 2,850,000 |                                                 | 0 2,850,000 |                                                                       | .00 503,294.00 |
| Student Services                      | Provost Administrative    | International Services                                  | 112,800     | 0           | 112,800                                         | 0           | 1,596.51                                                              | .00            |
| Administration                        | Units                     |                                                         |             |             |                                                 |             |                                                                       |                |
| Total Student Services Administration |                           |                                                         | 112,800     | 0           | 112,800                                         | 0           | 1,596.51                                                              | .00            |
| Items not in Exhibit                  | Computer Service          | Supplies_Expense                                        | 6,107,845   | 0           | 6,107,845                                       | 0           | 6,107,845.00                                                          | .00            |
| Sub-Total: Computer Service           |                           |                                                         | 6,107,845   | 0           | 6,107,845                                       | 0           | 6,107,845.00                                                          | .00            |
|                                       | Contingency               | Retirement                                              | 0           | 0           | 0                                               | 0           | 2,948.75                                                              | .00            |
|                                       |                           | Supplies_Expense                                        | 0           | 0           | 0                                               | 0           | (431,426.34)                                                          | .00            |
| Sub-Total: Contingency                |                           |                                                         | 0           | 0           | 0                                               | 0           | (428,477.59)                                                          | .00            |
|                                       | Fringe Benefits           | Accrued Annual Leave                                    | 0           | 0           | 0                                               | 0           | (402.72)                                                              | .00            |
|                                       |                           | Other Staff Benefits                                    | 247,645     | 0           | 238,491                                         | 0           | .00                                                                   | .00            |
|                                       |                           | Retirement                                              | 54,875      | 0           | 54,875                                          | 0           | 31,400.00                                                             | .00            |
|                                       |                           | Supplies_Expense                                        | 125         | 0           | (62,226)                                        | 0           | 1,268.20                                                              | .00            |
| Sub-Total: Fringe Benefits            |                           |                                                         | 302,645     | 0           | 231,140                                         | 0           | 32,265.48                                                             | .00            |
|                                       | Workstudy                 | Federal Workstudy Salaries                              | 0           | 334,000     | 0                                               | 334,000     | .00                                                                   | 148,076.00     |
|                                       |                           | State Workstudy Salaries                                | 0           | 450,000     | 0                                               | 450,000     | .00                                                                   | 267,451.00     |
| Sub-Total: Workstudy                  |                           |                                                         | 0           | 784,000     | 0                                               | 784,000     |                                                                       | .00 415,527.00 |
| Total Items not in Exhibit            |                           |                                                         | 6,410,490   | 784,000     | 6,338,985                                       | 784,000     | 5,711,632.89 415,527.00                                               |                |
| Total                                 |                           |                                                         |             |             |                                                 |             | 193,018,288 3,634,000 195,098,132 3,634,000 181,547,487.98 918,821.00 |                |

Run on: 09/14/2023
"""



messages = [
    ChatMessage(
        role="system", content=nSystem_prompt
    ),
    ChatMessage(role="user", content=markdown_data),
]

resp =llm.chat(messages)
resp
print(resp.dict()['raw']['content'][0]["text"])
