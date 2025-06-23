import os
from pypdf import PdfReader
from openai import OpenAI
import streamlit as st
import my_modules.open_ai_call as gi
import zipfile
import streamlit_mermaid as stmd

def main():
    #user_input = st.text_input("Please enter the file path")
    st.set_page_config(layout="wide")
    file = st.file_uploader("Pick a file")
    pr = st.button("Analyze")
    if pr == True:
        analyse(file)
        paint_on_ui()

def analyse(file):
    #reader = PdfReader("Bill_Pay_Requests.pdf")
    #reader = PdfReader("SOX_Compliance_Requirements_2024.pdf")
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"

    reader1 = PdfReader("SOX_Compliance_Requirements_2023.pdf")
    text1 = ""
    for page in reader1.pages:
        text1 += page.extract_text() + "\n"

    diff = gi.query(question="Summarize the difference between SOX 2023 and SOX 2024 processes", context=f"2023 SOX: {text}   2024 SOX: {text1}", role="analyst")
    print(diff)
    process_desc = gi.query(question="Give me step by step process with any conditional statements", context=text, role="analyst")
    process_doc = open("Process Documentation.txt", "w")
    process_doc.write(process_desc)
    process_doc.close()

    question = """Generate an xml with BPMN2.0 standards for this process. Name the process."""
    bpmn_file_content = gi.query(question=question, context=process_desc, role="expert programmer")

    #f = open("process_file.bpmn", "r")
    #bpmn_file_content = f.read()
    #f.close()

    #remove unwanted elements from the xml
    #print(bpmn_file_content)
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

    bpmn_file_content = bpmn_file_content[start_index:(end_index+14)]
    #print(bpmn_file_content)

    bpmn_file = open("process_file.bpmn", "w")
    bpmn_file.write(bpmn_file_content)
    bpmn_file.close()

    zipfile.ZipFile("process_file.zip", mode="w").write("process_file.bpmn")
    #take the bpmn file and ask for a mermaid code
    question = """Take this bpmn file content and generate a mermaid code. Use the following example:
     graph TD
    Start --> EvaluateCompliance
    EvaluateCompliance -->|Change Needed?| ChangeNeeded
    ChangeNeeded -->|Yes| MakeChange
    ChangeNeeded -->|No| PublishToManagement
    MakeChange --> End
    PublishToManagement --> End

    subgraph Approval Process
        Start[Start]
        EvaluateCompliance[Evaluate Compliance]
        ChangeNeeded{Change Needed?}
        MakeChange[Make Change]
        PublishToManagement[Publish to Management]
        End[End]
    end
       """
    status = "Generating image file........."
    st.write(status)
    mermaid_content = gi.query(question=question, context=bpmn_file_content, role="expert programmer")
    try:
        start_delim = '```mermaid'
        end_delim = '```'
        print("---------mermaid: OG-----------", mermaid_content, mermaid_content.find('```mermaid'), sep="\n")
        mermaid_content = mermaid_content[mermaid_content.find(start_delim)+len(start_delim):]
        print("---------mermaid: 1st transf-----------", mermaid_content, sep="\n")
        mermaid_content = mermaid_content[:mermaid_content.find(end_delim)]
        print("---------mermaid: 2nd transf-----------", mermaid_content, sep="\n")
    except Exception as e:
        print("Error file processing mermaid content")
    mer_file = open("process_mermaid.txt", "w")

    mer_file.write(mermaid_content)
    mer_file.close()
    status = "Preparing image......"
    #os.remove("process_file.bpmn")

def paint_on_ui():
    m_file = open("process_mermaid.txt", "r")
    txt = m_file.read()
    m_file.close()
    mmd = stmd.st_mermaid(txt, height="900px", width="100%")
    st.write(mmd)
    #js_code = "<script  type='module'> import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs'; mermaid.initialize({ startOnLoad: true }); </script> "
    #st.html('''{js_code}<div class="mermaid">{txt}</div>''')
    

if __name__ == "__main__":
    main()