
import ast
import openai
import streamlit as st


def insight(pre_prompt_gpt):

    prompt = pre_prompt_gpt+"""output example
       if question is relevant to the table then output:
       {'insight_name':'''sql query'''}
       if question is not relevant to the table then output:
       "1.No data found
        2.Irrelevant question"

        """
    completion = openai.ChatCompletion.create(
        engine="gpt4-8k",
        temperature=0,
        messages=[{'role': 'system', 'content': 'You are a business analytics insight generater'},
                  {"role": "user", "content": prompt}])

    output = completion["choices"][0]["message"]['content']
    print(
        '#####################insight_output####################################')
    print(output)
    #st.text(completion)
    if output.find('{') != -1:
        output_dict_str = output[output.find('{'):output.rfind('}')+1]
        output_dic = ast.literal_eval(output_dict_str)
        return output_dic
    else:

        st.markdown(f"### **{output}**", unsafe_allow_html=True)
        return {}
