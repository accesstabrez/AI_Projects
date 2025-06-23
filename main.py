from streamlit_float import *
import os
import streamlit as st
import my_modules.open_ai_call as gi
import my_modules.compare_files as cmf
import streamlit_mermaid as stmd 
import my_modules.screen_automation as sa
import random

SUPPORTED_BPM_TOOLS = ["IBM BAW CloudPak", "Camunda"]

# 1. Provide actionable options
# # - Compare two files
# # - Understand the process as steps
# # - Create a BPMN file


# 2. Based on the options selected, show the screen
css = """<style>
.footer {
position: fixed;
left: 250;
bottom: 50px;
width: 50%;
max-width: 20%;
max-height: 20%;
background-color: white;
color: black;
text-align: center;
}
.user-chat-bubble {
    background-color: #91ebb1;
    border-radius: 10px;
    padding: 10px;
    max-width: 300px;
    margin: 10px;
    align:left;
    position: relative;
    font-family: Arial, sans-serif;
}

.user-chat-bubble::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 20px;
    width: 0;
    height: 0;
    border: 10px solid transparent;
    border-top-color: #91ebb1;
    border-bottom: 0;
    margin-left: -10px;
    margin-bottom: -10px;
}
.bot-chat-bubble {
    background-color: #98ebf5;
    border-radius: 10px;
    padding: 10px;
    max-width: 300px;
    margin: 10px;
    position: relative;
    font-family: Arial, sans-serif;
    content: "./workflow.png";
}

.bot-chat-bubble::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 20px;
    width: 0;
    height: 0;
    border: 10px solid transparent;
    border-top-color: #98ebf5;
    border-bottom: 0;
    margin-left: 180px;
    margin-bottom: -10px;
}
</style>
<div class="footer">
    <img src="https://www.usbank.com/etc.clientlibs/ecm-global/clientlibs/clientlib-site/resources/images/svg/logo-personal.svg">
</div>
"""

def init():
    if "process_summary" not in st.session_state:
        st.session_state["process_summary"] = ""
    if "ques" not in st.session_state:
        st.session_state["ques"] = ""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'mesages' not in st.session_state:
        st.session_state.mesages = []
    st.markdown("""
        <style>
        label>div>p{
            font-weight: bold;
        }
        </style>
        """, unsafe_allow_html=True,
    )

def chat_content():
    st.session_state['contents'].append(st.session_state.content)

# Function to display chat messages
def display_chat():
    for message in st.session_state.chat_history:
        if message.startswith('User: '):
            st.markdown(f'<div class="user-chat-bubble">{message.split('User: ')[1]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-chat-bubble">{message}</div>', unsafe_allow_html=True)

# Function to handle new messages
def handle_message():
    print(st.session_state.new_message)
    if st.session_state.new_message == "clear":
        st.session_state.chat_history = []
        return
    if st.session_state.new_message:
        user_message = st.session_state.new_message
        st.session_state.chat_history.append(f"User: {user_message}")
        # Add a system response
        system_response = ["Sure, please wait while I make the change for you.", "Working on it, please wait....", "That's a good suggestion, allow me to make the change and get back."]
        st.session_state.chat_history.append(random.choice(system_response))
        if st.session_state["modification_scope"] == "Everything":
            cmf.apply_modification_to_all(project_name=st.session_state["project_name"], query=user_message)
        else:
           cmf.apply_modification_to_diagram(project_name=st.session_state["project_name"], query=user_message) 
        # st.session_state.new_message = ""

def main():
    init()
    file1, file2, comparision_summary, process_summary, ques, sidebar = None, None, None, None, None, None
    s1, s2 = st.sidebar.columns([1,2])
    s1.image('./workflow.png', width=50)
    s2.header("Process Generation")
    project_name = st.sidebar.text_input(label="Project Title: ", help="Please enter the project name for this work")
    st.session_state["project_name"] = project_name
    if project_name:
        sidebar = st.sidebar.radio('Action', ('Processify', 'Create a BPMN File', 'Compare process documentations'))
    
    if sidebar == "Compare process documentations":
        st.header("Compare")
        file1 = st.file_uploader("Existing process document")
        st.subheader("To")
        file2 = st.file_uploader("New process document")
        if file1 and file2:
            cm = st.button("Compare")
            if cm:
                comparision_summary = cmf.compare_files(file1, file2)
                if comparision_summary != None and comparision_summary != "":
                    st.session_state["comparision_summary"] = comparision_summary
        
        if "comparision_summary" in st.session_state:
            st.header("Summary of the difference:")
            comparision_summary = st.session_state["comparision_summary"]
            st.write(comparision_summary)
            st.download_button(label="Download", file_name=f"{project_name}_Process_Comparision.txt"
                            , data=comparision_summary
                            )
        
    elif sidebar == 'Processify':
        st.header(sidebar)
        main_col, chat_col = st.columns([3,1])
        file = main_col.file_uploader("Please upload the process document to analyze")
        if file:
            sb = main_col.button("Processify")
            if sb == True:
                process_summary, ques = cmf.summarize(file=file,project_name=project_name)
                st.session_state["process_summary"] = process_summary
                st.session_state["ques"] = ques
        if "process_summary" in st.session_state and st.session_state["process_summary"] != "":
            process_summary = st.session_state["process_summary"]
            ques = st.session_state["ques"]
            chat_col.subheader("Process Modification")
            st.session_state["modification_scope"] = chat_col.radio("Modification Scope", options=["Process Flow Diagram", "Everything"], index=0,horizontal=True)
            with chat_col:
                display_chat()
                st.chat_input("", on_submit=handle_message, key="new_message")
            with main_col:                
                st.header("Analysis")
                st.subheader("Process Summary")
                st.write(process_summary)
                st.subheader("Questions to ask:")
                st.write(ques)
                st.subheader("Workflow: ")
                st.write(cmf.paint_on_ui(project_name=project_name))
                st.download_button(label="Download", file_name=f"{project_name}_Process_documentation.txt"
                                , data=process_summary
                                )
            if main_col.button("Create a BPMN file for this process"):
                print("Using Process Summary 1")
                # print(process_summary)
                cmf.create_bpmn_file(process_summary=process_summary)
        with chat_col:
                st.markdown(css,unsafe_allow_html=True)    
    elif sidebar == 'Create a BPMN File':
        st.header(sidebar)
        main_col, chat_col = st.columns([3,1])
        file = main_col.file_uploader("Please upload the process to document and create bpmn for")
        compatibility_app = main_col.selectbox('Which tool do you want it to be compatible to?', options=SUPPORTED_BPM_TOOLS)
        if file or st.session_state["process_summary"]:
            if main_col.button("Generate BPMN"):
                if not file:
                    print("Using Process Summary")
                    bpmn_file_content = cmf.create_bpmn_file(process_summary=st.session_state["process_summary"], compatibility_app=compatibility_app,project_name=project_name)
                else:
                    bpmn_file_content = cmf.create_bpmn_file(file=file, compatibility_app=compatibility_app,project_name=project_name)
                st.session_state["bpmn_file_content"] = bpmn_file_content

            if "bpmn_file_content" in st.session_state:
                bpmn_file_content = st.session_state["bpmn_file_content"]
                main_col.success("BPMN and Zip file created successfully")
                with main_col.expander("View Generated File" ):
                    main_col.write(bpmn_file_content)
                col1, col2, col3 = main_col.columns(3)
                col1.download_button(label="Download BPMN", file_name=f"{project_name}_Process.bpmn"
                            , data=bpmn_file_content, type="primary", use_container_width=True
                            )
                with open(f"{project_name}_process_file.zip", 'rb') as f:
                    col2.download_button("Download Zip", f, file_name=f"{project_name}_process_file.zip", type="primary", use_container_width=True)
                if col3.button(label="Upload to BPM tool", type="primary"):
                    sa.upload_to_tool(compatibility_app)

if __name__ == "__main__":
    st.set_page_config(page_title='Process analysis and generation', page_icon = './workflow.png', layout = 'wide', initial_sidebar_state = 'auto')
    float_init(theme=True, include_unstable_primary=False)
    main()