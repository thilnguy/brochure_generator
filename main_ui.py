from collections import defaultdict
import os
import gradio as gr
from dotenv import load_dotenv

from brochure_generator import BrochureGenerator

load_dotenv()
USE_API = os.getenv("USE_API", "False").lower() in ("true", "1", "t")

models = defaultdict(dict)
if USE_API:
    load_dotenv()
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    from openai import OpenAI
    openai = OpenAI()

    # Store lightweight models for API
    models["api"]["get_link_relevant"] = ["gpt-4.1-mini", "gpt-3.5-turbo", "llama-2-7b-chat"]
    models["api"]["create_brochure"] = ["gpt-3.5-turbo", "gpt-4.1-mini", "llama-2-7b-chat"]

else:
    # Store lightweight models for Ollama
    models["ollama"]["get_link_relevant"] = ["llama3.2", "gpt-oss", "llama2:7b"]
    models["ollama"]["create_brochure"] = ["gpt-oss", "llama2:7b"]
    
source = "api" if USE_API else "ollama"
get_link_relevant_models_default = models[source]["get_link_relevant"][0]
create_brochure_models_default = models[source]["create_brochure"][0]

def start_loading():
    return gr.update(value="⏳ *Generating brochure… Please wait…*")

def stop_loading(result):
    return gr.update(value=""), result


with gr.Blocks(theme=gr.themes.Soft(), css="""
#header {
    text-align:center;
    font-size:32px;
    font-weight:700;
    padding: 10px;
    margin-bottom: 15px;
}
#subheader {
    text-align:center;
    font-size:16px;
    margin-bottom: 30px;
    color: #555;
}
.card {
    border: 1px solid #ddd; 
    padding: 20px;
    border-radius: 12px;
    background: white;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
}
""") as demo:

    # ----- Header -----
    gr.HTML("<div id='header'>📄 AI Brochure Generator</div>")
    gr.HTML("<div id='subheader'>Generate a clean, formatted brochure from any company website.</div>")

    # ----- Input Card -----
    with gr.Row():
        with gr.Column(scale=1):
            with gr.Group(elem_classes="card"):
                company_name_input = gr.Textbox(label="🏢 Company Name", placeholder="Enter the company name")
                url_input = gr.Textbox(label="🔗 Company URL", placeholder="Enter the company website URL")
                
                get_link_relevant_model_selector = gr.Dropdown(
                    label="🔍 Model for Extracting Relevant Links",
                    choices=models[source]["get_link_relevant"],
                    value=get_link_relevant_models_default,
                )

                create_brochure_model_selector = gr.Dropdown(
                    label="📝 Model for Creating Brochure",
                    choices=models[source]["create_brochure"],
                    value=create_brochure_models_default,
                )
                language_selector = gr.Dropdown(
                    label="🌐 Brochure Language",
                    choices=["English", "French", "Vietnamese"],
                    value="English")
                generate_button = gr.Button("✨ Generate Brochure", variant="primary")

                loading_indicator = gr.Markdown("")

        # ----- Output Card -----
        with gr.Column(scale=2):
            with gr.Group(elem_classes="card"):
                output_area = gr.Markdown(label="Generated Brochure")

    # ----- Examples Section -----
    gr.Examples(
        examples=[
            ["Hugging Face", "https://huggingface.co", get_link_relevant_models_default, create_brochure_models_default],
            ["Inria", "https://www.inria.fr/en/", get_link_relevant_models_default, create_brochure_models_default],
            ["OpenAI", "https://www.openai.com/", get_link_relevant_models_default, create_brochure_models_default]
        ],
        inputs=[company_name_input, url_input, get_link_relevant_model_selector, create_brochure_model_selector],
        label="Example Inputs"
    )

    # ----- Interactivity -----
    # Show "loading…" indicator
    generate_button.click(start_loading, outputs=loading_indicator, queue=False)

    # Run brochure generator
    def run_brochure_generator(company_name, url, language, get_link_relevant_model, create_brochure_model):
        generator = BrochureGenerator(company_name, url, language, get_link_relevant_model, create_brochure_model)
        return generator.generate()
    
    
    run_event = generate_button.click(
        fn=run_brochure_generator,
        inputs=[company_name_input, url_input, language_selector, get_link_relevant_model_selector, create_brochure_model_selector],
        outputs=[output_area],
    )

    # Hide loading message after done
    run_event.then(
        stop_loading,
        inputs=output_area,
        outputs=[loading_indicator, output_area],
    )

demo.launch(inbrowser=True)
