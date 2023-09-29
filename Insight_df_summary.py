
import streamlit as st
import openai
import matplotlib.pyplot as plt


def insight_df_summary(insight_title, df_insight, show_code, explain_code, question_prompt):

    prompt = """
    from following dataframe create textual summary. Use bullet points if there are multiple insights.
and give python code to generate most relevant type plot/chart using seaborn for better visualization of this data.
If data has single value then do not generate the plot.The plot should look refined and professional.
do not use scientific notations.convert axis range to Thousand, Million or Billion etc. 
If hues are present, color-coded legends must be included. Legend should not be overlapping on the graph. If there are more than 7 xticks, rotate them by 75 degree.
Do not overlap the plot/chart. enclose this python code in '{}'.
If no plot is generated then {} will be empty.
Results should contain textual summary and then python code in '{}'.
For example"
If textual summary and plot both then 
textual summary  
{
python code
}"
If there is only textual summary and no plot is generated then
textual summary  
{         

}"
The phrasing of the summary should consider the <"""+insight_title+""">.
If the data is not provided or the provided data has no values then give output as <NO DATA AVAILABLE FOR GIVEN QUESTION.>
Give more weightage to the insight title than the question while generating summary and plot code.
Insight Title: """+insight_title+"""
Question: """+question_prompt+"""
Data:
"""

    completion = openai.ChatCompletion.create(
        engine="gpt4-8k",
        temperature=0,
        messages=[{'role': 'system', 'content': 'You are a text summarizer '},
                  {"role": "user", "content": prompt+df_insight.to_csv(index=False)}])

    output = completion["choices"][0]["message"]['content']
    print(completion)
    #st.text(completion)
    # st.text(output)
    print('###################OUTPUT###################')
    print(output)
    output_summary = output[:output.find('{')]
    print('###################OUTPUT_SUMMARY###################')
    print(output_summary)

    st.write(output_summary)
    plot_code = output[output.find('{')+1:output.rfind('}')]
    print('###################PLOT CODE###################')
    print(plot_code)

    if plot_code.isspace():
        pass
    else:
        try:
            exec(plot_code)
            if show_code:
                st.markdown(
                    f"###### **{'Python code to visualize relevant data'}**", unsafe_allow_html=True)
                st.code(plot_code, language='python')

            if explain_code:
                with st.expander(f"###### **{'See code explaination'}**"):

                    prompt = """Explain the following python code  : """+plot_code
                    completion = openai.ChatCompletion.create(
                        engine="gpt4-8k",
                        # engine="chatgpt",
                        temperature=0,
                        messages=[{'role': 'system', 'content': 'Your job is to explain the code '},
                                  {"role": "user", "content": prompt}])

                    output = completion["choices"][0]["message"]['content']
                    st.write(output)

            return st.pyplot(plt.gcf())

        except:
            pass
