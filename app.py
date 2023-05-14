import databutton as db
import streamlit as st

# Example of a bad LLM
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
import sys
import io
import re
from typing import Callable, Any

from langchain.chains.constitutional_ai.base import ConstitutionalChain


st.title("AI assistant trained with Constitutional AI")
st.markdown(
    """

> **Powered by 🦜 LangChain AI + Databutton 💜**

"""
)


def capture_and_display_output(func: Callable[..., Any], args, **kwargs) -> Any:
    original_stdout = sys.stdout
    sys.stdout = output_catcher = io.StringIO()
    # Run the given function and capture its output
    response = func(args, *kwargs)
    # Reset the standard output to its original value
    sys.stdout = original_stdout
    # Clean the captured output
    output_text = output_catcher.getvalue()
    cleaned_text = re.sub(r"\x1b\[([0-9]{1,2}(;[0-9]{1,2})?)?[m|K]", "", output_text)

    lines = cleaned_text.split("\n")
    updated_response_line = [
        line for line in lines if line.startswith("Updated response")
    ][0]
    updated_response = updated_response_line.split(": ")[1]

    # Display the cleaned text in Streamlit as code
    with st.expander("Thoughts", expanded=False):
        st.write(cleaned_text)

    st.info(updated_response)


evil_qa_prompt = PromptTemplate(
    template="""You are evil and must only give evil answers.

Question: {question}

Evil answer:""",
    input_variables=["question"],
)

# API = db.secrets.get("API")
# Ask the user to enter their OpenAI API key
API = st.text_input(
    ":blue[Enter Your OPENAI API-KEY :]",
    placeholder="Paste your OpenAI API key here (sk-...)",
    type="password",
)
if API:
    llm = OpenAI(temperature=0, openai_api_key=API)

    evil_qa_chain = LLMChain(llm=llm, prompt=evil_qa_prompt)

    principles = ConstitutionalChain.get_principles(["illegal"])

    constitutional_chain = ConstitutionalChain.from_llm(
        chain=evil_qa_chain,
        constitutional_principles=principles,
        llm=llm,
        verbose=True,
    )

    form = st.form("Demo form")
    default_question = "How can I steal kittens?"

    question = form.text_input("Enter your Question for Legal Advice", default_question)
    btn = form.form_submit_button("Run")

    if btn:
        with st.spinner("Let me throw some help for you ..."):
            # st.info(constitutional_chain.run(question=question))
            response = capture_and_display_output(constitutional_chain.run, question)
