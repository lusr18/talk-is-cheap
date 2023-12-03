import os
from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain.llms import HuggingFaceHub
from langchain.prompts import PromptTemplate, FewShotPromptTemplate

load_dotenv()
huggingfacehub_api_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")

"""
Use HuggingFace Flan Model with Prompt
"""
def animal_analogies_flan_model(animal):
    repo_id = "google/flan-t5-xxl"
    llm = HuggingFaceHub(
        repo_id=repo_id,
        model_kwargs={"temperature": 0.9, "max_length": 64},
        huggingfacehub_api_token=huggingfacehub_api_token,
    )
    
    animal_home_examples = [
        {"animal": "bird", "home": "nest"},
        {"animal": "cat", "home": "litter box"}
    ]

    example_template = """\
    Animal: {animal}
    Home: {home}\
    """

    example_prompt = PromptTemplate(
        input_variables=["animal", "home"],
        template=example_template
    )

    few_shot_prompt = FewShotPromptTemplate(
        examples=animal_home_examples,
        example_prompt=example_prompt,
        prefix="Identify the home for the given animal",
        suffix="Animal: {animal}\nHome: ",
        input_variables=["animal"],
        example_separator="\n\n"
    )
    
    llm_chain = LLMChain(prompt=few_shot_prompt, llm=llm)
    return llm_chain.run(animal)


"""
Multi-chain example using gpt2 and google-flan-t5-xxl
"""
def multi_chain_gpt_flan():
    # Peform LLM
    repo_id = "gpt2"
    gpt_llm = HuggingFaceHub(
        repo_id=repo_id,
        model_kwargs={"temperature": 0.9, "max_length": 64},
        huggingfacehub_api_token=huggingfacehub_api_token,
    )
    
    gpt2_template = """Question: {question}

    Answer: Let's think step by step."""
    gpt2_prompt = PromptTemplate(template=gpt2_template, input_variables=["question"])
    gpt2_question = "How to send an email?"
    gpt2_chain = LLMChain(prompt=gpt2_prompt, llm=gpt_llm)
    gpt2_output = gpt2_chain.run(gpt2_question)
    
    print("-" * 50)
    print(gpt2_output)
    print("-" * 50)
    
    # Perform translation
    repo_id = "google/flan-t5-xxl"
    flan_llm = HuggingFaceHub(
        repo_id=repo_id,
        model_kwargs={"temperature": 0.9, "max_length": 64},
        huggingfacehub_api_token=huggingfacehub_api_token,
    )
    translation_template = "Translate English to French: {text}"
    translation_prompt = PromptTemplate(template=translation_template, input_variables=["text"])
    translation_input = {"text": gpt2_output}
    translation_chain = LLMChain(prompt=translation_prompt, llm=flan_llm)
    translated_output = translation_chain.run(translation_input)
    
    print("-" * 50)
    print(translated_output)
    print("-" * 50)
    


if __name__ == "__main__":
    # animal = "dog"
    # print(animal_analogies_flan_model(animal))
    
    multi_chain_gpt_flan()