
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import openai
import os
from dotenv import load_dotenv
from utils import decode_and_extract_text
import json
from fastapi.responses import FileResponse
from pydantic import BaseModel
import base64

load_dotenv()

app = FastAPI()

# OpenAI Azure Configuration
openai.api_type = "azure"
openai.azure_endpoint = os.getenv("AZURE_OPENAI_API_BASE")  # Base endpoint
openai.api_version = os.getenv("AZURE_OPENAI_API_VERSION")  # API version
openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")  # API key

# LLM response function
async def get_llm_response(prompt: str):
    """Call OpenAI Azure endpoint asynchronously to get the LLM response."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": prompt},
            ],
            temperature=1
        )
        return response.choices[0].message.content
    except Exception as e:
        raise RuntimeError(f"Failed to generate questions: {str(e)}")

# 1. Azure Architecture Document Creation with PaaS Services
class AzureArchitectureDocumentRequest(BaseModel):
    features_list_path: str
    bsns_stories_path: str
    enablmnt_stories_path: str

async def create_azure_architecture_document(request: AzureArchitectureDocumentRequest):
    with open(request.features_list_path, 'r') as fp:
        features_list = fp.read()
        
    with open(request.bsns_stories_path, 'r') as fp:
        bsns_stories = fp.read()
        
    with open(request.enablmnt_stories_path, 'r') as fp:
        enablmnt_stories = fp.read()

    az_sol_doc_prompt = f"""You are a 'AZURE SOLUTIONS ARCHITECT', dedicated to assisting users in developing effective Azure solutions.

    Your task is to generate an 'AZURE ARCHITECTURE DOCUMENT' using PaaS services based on the provided list of Features, Business Stories, and Enablement Stories. 

    Consider the following points for generating Azure Architecture Document.
    ## Solution Architecture
    ## Network Architecture
        a. Solution communication flow between the components and other systems which are integrated
        b. Whitelisting of certain IPs as access to the public end points of the resources will be restricted from Internet
        c. Source and Destination communication matrix
    ## Storage Architecture
    ## Backup and Disaster Recovery Architecture
    ## Security Architecture
        a. Details on securing the solution at Network Level - using Azure services need to be detailed.
        b. Details on securing the data of the solution- (Example: Data in transit, data at Rest, data encryption, masking etc.) need to be detailed.
        c. Details on Identity and Access Requirements for all the components used in the solution architecture – RBAC (at all levels of the enterprise from network access control at the device level, database access control at the data level, application level access control, as well as user access), SPN, Key Vaults, Access Keys etc.
        d. Certificate Requirements
    ## Environment Details
        a. Resources and their specifications along with cost is required in Production Azure Subscription.
        b. Resources and their specifications along with cost is required in Staging Azure Subscription.
        c. Resources and their specifications along with cost is required in DevTest Azure Subscription.
    ## Monitoring Architecture
        a. Azure Monitoring
        b. Log Analytics
        c. Application Insights
        d. Diagnostic settings
    ## Deployment Architecture
        a. ARM template, PS, DSC, CLI etc. 
        b. DevOps - Repos, Service Connection, Build and Release Pipelines.
        c. Slots for Prod and Pre-Prod.
    ## Integrations
        a. Integration with other systems
        b. Source and Destination communication matrix


    The 'Azure Architecture Document' MUST cover the following and other required details:
    - Overview of the architecture
    - Detailed descriptions of each PaaS service used
    - Justification for choosing each service
    - Integration points between services
    - Security considerations
    - Scalability and performance considerations
    - Best practices for architecture design as recommended by leading firms

    Please consider the following user INPUTS:
    List of Features : {features_list}
    Business Stories : {bsns_stories}
    Enablement Stories : {enablmnt_stories}

    MUST Return the output in text format with all the above 'REQUIREMENTS'
    """

    
    response = await get_llm_response(az_sol_doc_prompt)

    with open("azure_architecture_document.txt", "w") as fp:
        fp.write(response)

    return {"document": response, "document_path": "azure_architecture_document.txt"}


# 2. Azure Logical Architecture Image
class AzureLogicalArchitectureImageRequest(BaseModel):
    architecture_document_path: str

async def create_azure_logical_architecture_image(request: AzureLogicalArchitectureImageRequest):
    with open(request.architecture_document_path, 'r') as fp:
        azure_logical_ar_doc = fp.read()
        
    az_logical_ar_dig_prompt = f"""You are an EXPERT in generating Azure Logical Architecture diagrams for software applications based on the user-provided architecture document. You possess the expertise of an Azure Solutions Architect, specializing in designing and creating clear, high-quality Azure Logical Architecture diagrams.

    Task:
    Your task is to generate only an image of the Azure Logical Architecture diagram based on the user-provided input.

    Requirements:
    Diagram Content:
        - Include all relevant PaaS services and their interactions.
        - Clearly depict the data flow between services.
        - Highlight security boundaries.
        - Represent the high-level network topology (e.g., VNets, subnets, gateways).
        - Adhere to best practices for Azure Logical Architecture design.
    Clarity:
        - The diagram must be clear, visually organized, and easy to understand.
        - Include all essential details so it can be later converted into Draw.io code.

    Input:Analyze the provided user input (architecture document):
    {azure_logical_ar_doc}


    Output:
        - Deliver only an image of the Azure Logical Architecture diagram.
        - Do not include any additional text, explanations, or annotations outside the diagram.
    Deliverable:
    A high-quality image representing the Azure Logical Architecture, fulfilling all the specified requirements.
    """
    
    response = await get_llm_response(az_logical_ar_dig_prompt)
    # Save the response to an image file

    image_path = "azure_logical_architecture_image.png"
    with open(image_path, "wb") as fp:
        fp.write(response.encode())

    # return FileResponse("azure_logical_architecture_image.png")
    return {
        "image": FileResponse(image_path, media_type="image/png"),
        "image_path": image_path
    }



# 3. Azure Logical Architecture Image in Draw.io Format
class AzureLogicalArchitectureDrawioRequest(BaseModel):
    architecture_document_path: str
    azure_logical_architecture_image: str

with open("temp_drawio.drawio", 'r') as fp:
    logical_arc_code = fp.read()

async def create_azure_logical_architecture_drawio(request: AzureLogicalArchitectureDrawioRequest):

    with open(request.architecture_document_path, 'r') as fp:
        architecture_document = fp.read()
        
    with open(request.azure_logical_architecture_image_path, 'rb') as fp:
        azure_logical_architecture_image = fp.read()
        
    image_base64 = base64.b64encode(azure_logical_architecture_image).decode('utf-8')

    az_lgcl_arc_prompt = f"""You are an EXPERT in generating DRAW.io XML code for Azure Logical Architectures. 
    As an Azure Solutions Architect, you are well-versed in Azure services, design principles, and best practices for logical architecture diagrams.
    Task:
    Your role is to generate a file with the **.drawio** extension containing the XML code for the Azure Logical Architecture provided by the user.
    Requirements:
    - Include all necessary details, such as:
        a. Service Icons: Represent Azure services accurately with appropriate icons or shapes.
        b. Data Flow Arrows: Depict data flow and connections between components.
        c. Annotations: Highlight security boundaries, network topology, and relevant architecture details.
        d. Best Practices: Follow standard guidelines for logical diagram creation to ensure clarity and professionalism.
    - Analyze and understand the provided example DRAW.io code to replicate its structure and style for the user's input.

    Following are the User provided Azure logical Architecture Details:
    architecture document: "{architecture_document}"
    azure logical architecture image : ![](data:image/png;base64,{image_base64})

    Example Reference:
    ```
    {logical_arc_code}
    ```
    Output Instructions:
        - MUST Generate only a file in the .drawio format containing the corresponding XML code.
        - Ensure the file represents the user's Azure Logical Architecture comprehensively and accurately.
        - Do not include any additional text or explanations in the output.
    """
    
    response = await get_llm_response(az_lgcl_arc_prompt)
    # Save the response to a drawio file
    with open("azure_logical_architecture_drawio.drawio", "w") as fp:
        fp.write(response)

    return FileResponse("azure_logical_architecture_drawio.drawio")




# 4. Create a UML Diagram in XML Based on the Azure Architecture Document
class UMLDiagramRequest(BaseModel):
    architecture_document_path: str
    # class_dig_code_path: str
    # component_dig_code_path: str
    # seq_dig_code_path: str

with open("UmL_class.drawio", 'r') as fp:
    class_dig_code = fp.read()

with open("UML_compnnt.drawio", 'r') as fp:
    component_dig_code = fp.read()
    
with open("UML_seq.drawio", 'r') as fp:
    seq_dig_code = fp.read()

async def create_uml_diagram(request: UMLDiagramRequest):
    with open(request.architecture_document_path, 'r') as fp:
        azure_logical_ar_doc = fp.read()
        
    uml_dig_prompt = f"""You are an EXPERT in generating DRAW.io XML code for UML diagrams based on the Azure Architecture Document provided by the user. You possess the expertise of a Software Engineer with advanced skills in designing and creating UML diagrams tailored to Azure architecture.
    Task: Your task is to generate a file with the .drawio extension containing the XML code for the UML diagram based on the user-provided Azure Architecture Document.
    Requirements:
        a) Diagram Types:
            - Class Diagrams: Represent key components, including attributes and methods.
            - Sequence Diagrams: Show major interactions between components and services.
            - Component Diagrams: Highlight service interactions and their roles within the architecture.
        b) Best Practices:
            1) Ensure the diagrams are clear, well-structured, and adhere to UML standards.
            2) Accurately represent relationships, dependencies, and interactions.
            3) Use intuitive naming conventions and visually logical layouts.

    Input:
    Azure Architecture Document:
    {azure_logical_ar_doc}

    Reference Example:
    Use the following example DRAW.io XML code as a guide for structure and format:
    Class Diagrams:
    ```{class_dig_code}```
    Sequence Diagrams:
    ```{seq_dig_code}```
    Component Diagrams:
    ```{component_dig_code}```

    Output:
    MUST return the UML diagram as a single **.drawio** file containing the XML code.
    Provide no additional text or explanation beyond the file.
    """
    
    response = await get_llm_response(uml_dig_prompt)
    # Save the response to a drawio file
    with open("uml_diagram.drawio", "w") as fp:
        fp.write(response)

    return FileResponse("uml_diagram.drawio")

# 5. Create an Image of Conceptual Architecture Based on Documents, Not Based on Azure
class ConceptualArchitectureImageRequest(BaseModel):
    brd_path: str
    features_path: str
    bsns_stories_path: str
    enablmnt_stories_path: str

async def create_conceptual_architecture_image(request: ConceptualArchitectureImageRequest):
    with open(request.brd_path, 'r') as fp:
        brd_doc = fp.read()
        
    with open(request.features_path, 'r') as fp:
        features_list = fp.read()
        
    with open(request.bsns_stories_path, 'r') as fp:
        bsns_stories = fp.read()
        
    with open(request.enablmnt_stories_path, 'r') as fp:
        enablmnt_stories = fp.read()


    cncpt_ar_dig_prompt = f"""You are an EXPERT in generating Conceptual Architecture diagrams for software applications based on user-provided input, including Business Requirements Documents, features lists, business stories, and enablement stories. You have the expertise of a Software Engineer specializing in designing and creating clear, high-level conceptual architecture diagrams.
    Task:
    Your task is to generate an image of the Conceptual Architecture diagram for the provided user input.
    Guidelines:
        a) Focus Areas:
            - High-level components and their interactions.
            - Representation of key business processes.
            - Major data flows between components.
            - Abstract depiction of the system, avoiding specific technology details.
            - Adherence to best practices for conceptual architecture design.
        b) Purpose: The diagram should provide a clear and understandable representation of the system's conceptual architecture.
        Ensure the diagram can be later converted into Draw.io code, so include all essential details and structure.
        Input:


    Analyze the user-provided details:
        - Business requirements document : {brd_doc}
        - features list : {features_list}
        - business stories : {bsns_stories}
        - enablement stories : {enablmnt_stories}

    Output:
    MUST return a clear and well-structured image of the Conceptual Architecture diagram.
    The image should exclusively represent the Conceptual Architecture without any additional text or explanation.
    """
    # Reference:
    # Use the following example conceptual architecture diagram, provided in base64 format, as a guide for structure and design:{image_input}
    
    response = await get_llm_response(cncpt_ar_dig_prompt)
    # Save the response to an image file
    with open("conceptual_architecture_image.png", "wb") as fp:
        fp.write(response.encode())

    return FileResponse("conceptual_architecture_image.png")



# 6. Conceptual Architecture in Draw.io Format
class ConceptualArchitectureDrawioRequest(BaseModel):
    conceptual_architecture_image_path: str

async def create_conceptual_architecture_drawio(request: ConceptualArchitectureDrawioRequest):
    with open(request.conceptual_architecture_image_path, 'r') as fp:
        conceptual_architecture_image = fp.read()

    with open("concpt_arc_dig.drawio", 'r') as fp:
        cncpt_ar_code = fp.read()

    image_base64 = base64.b64encode(conceptual_architecture_image).decode('utf-8')
        
    cncpt_ar_code_Prompt = f"""You are an EXPERT in generating DRAW.io code for Conceptual Architecture diagrams. The user is in the initial phase of building a software application and aims to create high-level Conceptual Architecture diagrams. Your role is to assist the user by generating DRAW.io code based on the provided image or description of the conceptual architecture. This will allow the user to edit the diagram further.

    Task:
    Your task is to generate a file with the .drawio extension containing the DRAW.io code for the user-provided architecture diagram.

    Requirements:
        a) Diagram Features:
            - Include high-level components.
            - Represent major data flows clearly.
            - Provide annotations for key business processes.
            - Follow best practices for creating clear and editable diagrams.
    Reference Example: Use the following example .drawio code for a sample conceptual architecture diagram as a guide:```{cncpt_ar_code}```

    Input:
    Analyze the user-provided conceptual architecture image: ![](data:image/png;base64,{image_base64})

    Output:
        - MUST Return a file with the **.drawio** extension that contains the complete and editable DRAW.io code for the user's conceptual architecture.
        - Do not include any additional text, explanations, or annotations outside the .drawio file.
    """
    
    response = await get_llm_response(cncpt_ar_code_Prompt)
    # Save the response to a drawio file
    with open("conceptual_architecture_drawio.drawio", "w") as fp:
        fp.write(response)
        
    return FileResponse("conceptual_architecture_drawio.drawio")

# Define API routes
@app.post("/create-azure-architecture-document")
async def create_azure_architecture_document(request: AzureArchitectureDocumentRequest):
    return await create_azure_architecture_document(request)

@app.post("/create-azure-logical-architecture-image")
async def create_azure_logical_architecture_image(request: AzureLogicalArchitectureImageRequest):
    return await create_azure_logical_architecture_image(request)

@app.post("/create-azure-logical-architecture-drawio")
async def create_azure_logical_architecture_drawio(request: AzureLogicalArchitectureDrawioRequest):
    return await create_azure_logical_architecture_drawio(request)

@app.post("/create-uml-diagram")
async def create_uml_diagram(request: UMLDiagramRequest):
    return await create_uml_diagram(request)

@app.post("/create-conceptual-architecture-image")
async def create_conceptual_architecture_image(request: ConceptualArchitectureImageRequest):
    return await create_conceptual_architecture_image(request)

@app.post("/create-conceptual-architecture-drawio")
async def create_conceptual_architecture_drawio(request: ConceptualArchitectureDrawioRequest):
    return await create_conceptual_architecture_drawio(request)


