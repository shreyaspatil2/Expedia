def Upload():

    import pandas as pd
    import streamlit as st
    from pandasql import sqldf

    from Insight import insight
    from Insight_df_summary import insight_df_summary

    import openai
    endpoint = 'https://allbirds.openai.azure.com/'
    region = 'eastus'
    key = 'd67d19908eba4902af4903c270547bba'
    openai.api_key = key
    openai.api_base = endpoint
    openai.api_type = 'azure'
    openai.api_version = "2023-03-15-preview"

    # Use the file_uploader to allow users to upload files
    uploaded_files = st.sidebar.file_uploader(
        "Upload Files", accept_multiple_files=False, type='csv')

    if uploaded_files:

        df = pd.read_csv(uploaded_files, encoding_errors='ignore')
        df_col_dtype = pd.DataFrame(df.dtypes)
        df_col_dtype = df_col_dtype.reset_index()
        df_col_dtype.columns = ['column', 'dtype']
        st.sidebar.dataframe(df_col_dtype, hide_index=True)
        columns = df.columns.to_list()
        col_str = ', '.join(columns)
        # st.dataframe(df.sample(5), height=220)
        sample_df = df.sample(10, ignore_index=True)
        st.dataframe(sample_df, height=220)

        # user_prompt = st.text_input(
        #     "Any instruction or comments (Optional):", key="sql_prompt")
        # user_prompt = user_prompt + " "
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
                        """If the question is not relevant to the table provided give output as "Irrelenat question".give output in the form of dictionary where key will be name of the insight and value will be <sql query to run using pandasql module of python>. following is a sample from actual dataset for your referene : \n""" + \
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
                            insight_df = sqldf(v, locals())

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
