from openai import OpenAI
import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()
key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=key)

def get_embedding(text, model="text-embedding-3-small", max_tokens=8192):
    text = text.replace("\n", " ")
    response = client.embeddings.create(input=[text], model=model)
    return response.data[0].embedding

def query(question, context, role):
    # print(question, context,role, sep="-------------\n")
    with st.spinner("Please wait, we are working on it.................."):
        """
        question_embedding = get_embedding(question)

        def fn(page_embedding):
            return np.dot(page_embedding, question_embedding)
        
        distance_series = df['embedding'].apply(fn)
        score_series = df['distance'] / df['distance'].max()

        top_four = distance_series.sort_values(ascending=False).index[0:4]
        top_four = distance_series.nlargest(4).index.tolist()

        text_series = df.loc[top_four]['text ']
        context = "\n".join(text_series)
        """
        example = ""
        
        content = f"You are an {role}. Please provide precise response and ask any questions that may help you refine the code.\
                Please always add the xml metadata/version tag at the begining like this: <?xml version=\"1.0\" encoding=\"UTF-8\"?>. You will use IBM BAW to implement this process.\
                Define process steps as user tasks, preferably in different swinlanes.\
                Please ensure the decision gateways have a sourceRef and targetRef attribute linking process steps sequentially.\
                create an extensive process inluding all process steps.\
                All given process steps must be included.\
                "
        
        if role == "Expert Camunda Programmer":
            f = open("sample_mermaid.txt", "r")
            example = f.readlines()
            f.close()
            example.insert(0, "The following mermaid file: ```" )
            example.append("```\n generates this bpmn: ```")
            f = open("Sample.bpmn", "r")
            example.append(f.readlines())
            example.append("```")
            f.close()
            content = f"You are an {role}. Make your response compatible to camunda web modeller."
        else:
            f = open("SOX_Process.txt", "r")
            example = f.readlines()
            example.insert(0, "The following mermaid file: ```" )
            example.append("```\n generates this bpmn: ```")
            f = open("SOX Approval Process.bpmn", "r")
            example.append(f.readlines())
            example.append("```")
            f.close()

        if example != "":
            content += f"Here is an example:{example}"
        # print(example)
        if role.lower() == "analyst":
            content = f"You are an {role}. Please provide detailed and precise response as bullet points. Do not add special formatting to the response."
        messages = [
                {"role":"system", "content": f"{content}"},
                {"role": "user", "content": question},
                {"role": "assistant", "content": f"Use this information to answer the user question: {context}. Please stick to this context when answering the question."}
            ]
        print(messages)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            #model=os.getenv("GPT_MODEL"),
            messages=messages)

    print('','','',sep='\n')
    print(response.choices[0].message.content)
    return response.choices[0].message.content