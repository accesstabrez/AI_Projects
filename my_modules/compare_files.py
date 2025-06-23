import my_modules.open_ai_call as gi
import streamlit.components.v1 as components

import time
import os
import streamlit as st
import zipfile
from pypdf import PdfReader
import streamlit_mermaid as stmd
def return_text_from_file(file):
    text = ""
    pages = PdfReader(file).pages
    for page in pages:
        text += page.extract_text() + "\n"
    return text

def compare_files(file1, file2):
    diff = gi.query(question="Understand the processes in these files. Highlight the difference in the \
                    process outlined by these two files. Outline the differences as bullet points in a way that it can be understood \
                    by a process analyst who can modify an existing process. "
                    , context=f"Existing process: {return_text_from_file(file1)}  New Process: {return_text_from_file(file2)}"
                    , role="analyst")
    return diff

def summarize (file=None, project_name="", modification_query="", process_desc=""):
    progress_bar = st.progress(0, "Starting interpretation.....")
    if process_desc is None or process_desc == "":
        process_desc = return_text_from_file(file)
    process_desc = gi.query(question="Give me step by step process with any conditional statements.\
                            Ask any questions that may help the developer build a process diagram.\
                            Define the process in at least 6 steps.\
                            Provide the response in 2 parts - Process Steps and Questions"
                            , context=process_desc, role="analyst")
    progress_bar.progress(34, "Writing information on server.......")
    process_doc = open(f"{project_name}ProcessDocumentation.txt", "w")
    process_doc.write(process_desc)
    process_doc.close()
    questions = ""
    split_process_desc = process_desc.split('Questions:')
    if split_process_desc and len(split_process_desc) == 2:
        questions = split_process_desc[1]
        process_desc = split_process_desc[0]
    progress_bar.progress(50, "Requesting workflow diagram.......")
    get_mermaid_diagram(process_desc=process_desc, project_name=project_name)
    progress_bar.progress(100, "Painting.........")
    time.sleep(1)
    progress_bar.empty()
    return process_desc, questions

def create_bpmn_file(project_name = "", file = None, process_summary = None, compatibility_app="IBM BAW CloudPak"):
    progress_bar = st.progress(0, "Initializing process.....")
    print(process_summary)
    if file:
        txt = return_text_from_file(file=file)
        progress_bar.progress(10, "Summarizing the process document")
        process_summary, ques = summarize(file)
    if process_summary:
        progress_bar.progress(40, "Requesting bpmn file")
        question = """Generate an xml with BPMN2.0 standards for this process. Name the process."""
        role = "Expert IBM BAW Developer"
        if compatibility_app == "Camunda":
            role = "Expert Camunda Programmer"
        bpmn_file_content = gi.query(question=question, context=process_summary, role=role)
        progress_bar.progress(70, "Preparing and writing content on server")
        start_index = 0
        end_index = len(bpmn_file_content)
        try:
            start_index = bpmn_file_content.index("<?xml")
        except ValueError as e:
            print("xml tag not found")

        try:
            end_index = bpmn_file_content.index("</definitions>")
        except ValueError as e:
            print("def tag not found")
        # print("Got result")
        bpmn_file_content = bpmn_file_content[start_index:(end_index+14)]
        bpmn_file = open(f"{project_name}_process_file.bpmn", "w")
        bpmn_file.write(bpmn_file_content)
        bpmn_file.close()
        progress_bar.progress(85, "Creating zip File")
        zipfile.ZipFile(f"{project_name}_process_file.zip", mode="w").write(f"{project_name}_process_file.bpmn")
        progress_bar.progress(100, "Ready!!!")
        time.sleep(1)
        progress_bar.empty()
        return bpmn_file_content
    else:
        print("invalid input. Exiting........")
        exit()

def get_mermaid_diagram(process_desc, project_name, modification_query = ""):
    question = modification_query + """. Take this context and generate a complete mermaid code. Always return the mermaid code within ```. Use the following example:
    graph TD
    Start --> InitiateSOXComplianceTeam
    InitiateSOXComplianceTeam --> DefineComplianceRequirements
    DefineComplianceRequirements --> ImplementInternalControls
    ImplementInternalControls --> ConductRegularSOXAudits
    ConductRegularSOXAudits -->|Deficiencies Identified?| DeficienciesIdentified
    DeficienciesIdentified -->|Yes| RectifyDeficiencies
    RectifyDeficiencies --> PrepareAnnualReports
    DeficienciesIdentified -->|No| PrepareAnnualReports
    PrepareAnnualReports --> ValidateReportsWithIndependentAuditors
    ValidateReportsWithIndependentAuditors --> End

    subgraph SOX Compliance Process
        Start[Start]
        InitiateSOXComplianceTeam[Initiate SOX Compliance Team]
        DefineComplianceRequirements[Define Compliance Requirements]
        ImplementInternalControls[Implement Internal Controls]
        ConductRegularSOXAudits[Conduct Regular SOX Audits]
        DeficienciesIdentified{Deficiencies Identified?}
        RectifyDeficiencies[Rectify Deficiencies]
        PrepareAnnualReports[Prepare Annual Reports]
        ValidateReportsWithIndependentAuditors[Validate Reports with Independent Auditors]
        End[End]
    end
    """
    mermaid_content = gi.query(question=question, context=process_desc, role="analyst")
    try:
        start_delim = '```'
        if os.getenv("GPT_MODEL") == "gpt-4":
            start_delim = '```'
        end_delim = '```'
        # print("---------mermaid: OG-----------", mermaid_content, mermaid_content.find('```mermaid'), sep="\n")
        mermaid_content = mermaid_content[mermaid_content.find(start_delim)+len(start_delim):]
        # print("---------mermaid: 1st transf-----------", mermaid_content, sep="\n")
        mermaid_content = mermaid_content[:mermaid_content.find(end_delim)]
        # print("---------mermaid: 2nd transf-----------", mermaid_content, sep="\n")
        mermaid_content = mermaid_content.replace("�", "")
        print("------after all replacements", mermaid_content, "-----", sep="\n")
    except Exception as e:
        print("Error file processing mermaid content")
    #if not os.path.exists(f"{project_name}_process_mermaid.txt"):
    mer_file = open(f"{project_name}_process_mermaid.txt", "w+")
    mermaid_content = mermaid_content.replace("’", "'")
    mer_file.write(mermaid_content)
    mer_file.close()

def paint_on_ui(project_name):
    m_file = open(f"{project_name}_process_mermaid.txt", "r")
    txt = m_file.read()
    m_file.close()
    mmd = stmd.st_mermaid(txt, height="900px", width="100%", )
    # custom_css = """
    # <style>
    # .mermaid {
    #     background-color: #f0f0f0;
    #     border-radius: 10px;
    #     padding: 10px;
    #     font-family: Arial, sans-serif;
    # }
    # </style>
    # """
    # components.html(f"""
    #     {custom_css}
    #     <div class="mermaid">
    #         {txt}
    #     </div>
    #     <script type="module">
    #         import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
    #         mermaid.initialize({{ startOnLoad: true }});
    #     </script>
    #     """, height=400)
    return mmd

def apply_modification_to_diagram(project_name, query):
    m_file = open(f"{project_name}_process_mermaid.txt", "r")
    txt = m_file.read()
    m_file.close()
    get_mermaid_diagram(modification_query=query, process_desc=txt, project_name=project_name)

def apply_modification_to_all(project_name, query):
    m_file = open(f"{project_name}ProcessDocumentation.txt", "r")
    txt = m_file.read()
    m_file.close()
    summarize(modification_query=query, process_desc=txt, project_name=project_name)