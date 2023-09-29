#  DATABRICKS_HOST =load_dotenv['DATABRICKS_HOST']
#     DATABRICKS_TOKEN = load_dotenv['DATABRICKS_TOKEN']
#     API_endpoint = load_dotenv['API_endpoint']

#     endpoint = load_dotenv['endpoint']
#     region = load_dotenv['region']
#     key = load_dotenv['key']

def csv_databricks():
    import pandas as pd
    import streamlit as st
    from pandasql import sqldf
    from Insight import insight
    from Insight_df_summary import insight_df_summary
    import openai
    from databricks_api import DatabricksAPI
    import requests
    import json
    import tempfile
    #from dotenv import load_dotenv
    #load_dotenv()
    DATABRICKS_HOST = "https://adb-1906126219572501.1.azuredatabricks.net"
   
    DATABRICKS_TOKEN = "dapica7a3c3b4a5fd03ffe9eac2b42855517-2"

    API_endpoint = "https://adb-1906126219572501.1.azuredatabricks.net/driver-proxy-api/o/1906126219572501/0821-144959-q6m0l5jm/7778/"

    endpoint = 'https://allbirds.openai.azure.com/'
    region = 'eastus'
    key = 'd67d19908eba4902af4903c270547bba'
    openai.api_key = key
    openai.api_base = endpoint
    openai.api_type = 'azure'
    openai.api_version = "2023-03-15-preview"
    db = DatabricksAPI(host=DATABRICKS_HOST, token=DATABRICKS_TOKEN)


    def res(query=str):
        response = requests.request(method='POST',
                                    headers={
                                        'Authorization': f'Bearer {DATABRICKS_TOKEN}'},
                                    url=API_endpoint,
                                    data=query)
        return response.content



    
    # Use the file_uploader to allow users to upload files
    file = st.sidebar.file_uploader(
        "Upload Files", accept_multiple_files=False, type='csv')

    if file is not None:
        file_details = {"FileName": file.name, "FileType": file.type}
       

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(file.read())
            file_path = temp_file.name

   
        db.dbfs.put(path=f"dbfs:/FileStore/csv_data/{file.name}",
                    src_path=file_path,
                    overwrite=True)
        response = res(file.name)
        generated_text = json.loads(response)
        print(generated_text)
        df_col_dtype_dict = generated_text["df_col_dtype_dict"]
        df_col_dtype = pd.DataFrame(df_col_dtype_dict)
        st.markdown(f"###### **{'Sample Data'}**", unsafe_allow_html=True)
        st.sidebar.dataframe(df_col_dtype, hide_index=True)
        sample_df_dict = generated_text["sample_df_dict"]
        sample_df = pd.DataFrame(sample_df_dict)
        st.dataframe(sample_df, height=220)
        columns = df_col_dtype.columns.to_list()
        col_str = ', '.join(columns)
        user_prompt = " "
        if user_prompt:
            with st.spinner('Wait for it ...'):
                col_str += col_str+user_prompt

        with st.form("plot_form"):
            question_prompt = st.text_input(
                "Ask Question:", key="question_prompt")
            col1, col2, col3 = st.columns(3)

            plot_submit = col1.form_submit_button(
                "Generate Insights")

            show_code = col2.checkbox('Show the code')
            explain_code = col3.checkbox('Explain the code')

        if plot_submit:

            with st.spinner('Wait for it...Generating the insight and plots...'):

                pre_prompt_gpt = """Give relevant insights from the dataframe df with columns """+col_str+""" .based on the following question :"""+question_prompt +\
                    """If the question is not relevant to the table provided give output as "Irrelenat question".give output in the form of dictionary where key will be name of the insight and value will be <sql query to run using pyspark sql module of python>. following is a sample from actual dataset for your referene : \n""" + \
                    sample_df.to_csv(index=False)

                output_dic = insight(pre_prompt_gpt)

                if output_dic:

                    print(
                        '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@DICTIONARY@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
                    print(output_dic)

                    for k, v in output_dic.items():
                        print(
                            '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@VALUE@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
                        print(v)

                        # st.text(k)
                        # st.text(v)

                        # insight_df = sqldf(v, locals())
                        # insight_df = pd.DataFrame()

                        response = res(v)
                        generated_text = json.loads(response)
                        # st.text(generated_text)
                        result_df_dict = generated_text["result_df_dict"]
                        result_df = pd.DataFrame(result_df_dict)
                        # st.dataframe(result_df, height=220)
                        insight_df = result_df
                        print(
                            '***********************************q_to_df***********************************')
                        print(insight_df)
                        if not insight_df.empty:

                            try:

                                st.markdown(
                                    f"### <u>**{(k).replace('_',' ').title()}**</u>", unsafe_allow_html=True)
                                if show_code:

                                    st.markdown(
                                        f"###### **{'SQL query to fetch relevant data'}**", unsafe_allow_html=True)
                                    st.code(
                                        v, language='sql')

                                if explain_code:
                                    with st.expander(f"###### **{'See code explaination'}**"):

                                        prompt = """Explain the following query : """+v
                                        completion = openai.ChatCompletion.create(
                                            engine="gpt4-8k",
                                            # engine="chatgpt",
                                            temperature=0,
                                            messages=[{'role': 'system', 'content': 'Your job is to explain the code '},
                                                      {"role": "user", "content": prompt}])

                                        output = completion["choices"][0]["message"]['content']
                                        st.write(output)

                                insight_df_summary(
                                        k, insight_df, show_code, explain_code, question_prompt)

                            except openai.error.InvalidRequestError as r:
                                st.text(r)
                                print(
                                    'Relevant data exceeded token limit')
                                st.markdown(
                                    f"### **Relevant data exceeded token limit**", unsafe_allow_html=True)
                            except Exception as e:
                                st.text(e)
                                print(
                                    'Something went wrong')
                                st.markdown(
                                    f"### **Something went wrong**", unsafe_allow_html=True)
                        else:
                            st.markdown(
                                f"### **No data available relevent to this query**", unsafe_allow_html=True)
                            print(
                                '********************************EMPTY DATAFRAME************')
#################################################################
