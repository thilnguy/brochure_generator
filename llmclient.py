import os
from openai import OpenAI
import json


class LLMClient:
    """A client to interact with a language model API."""
    
    def __init__(self, get_link_relevant_model=None, generate_brochure_model=None):
        # Determine whether to use OpenAI API or Ollama
        use_api = os.getenv("USE_API", "False").lower() in ("true", "1", "t")

        if use_api:
            # OpenAI setup
            self.llm_client = OpenAI()
            default_models = {
                "get_relevant_links_model": os.getenv("API_GET_RELEVANT_LINK_MODEL", "gpt-4_mini"),
                "generate_brochure_model": os.getenv("API_GENERATE_BROCHURE_MODEL", "gpt-4_mini"),
            }
        else:
            # Ollama setup
            ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
            self.ollama_base_url = ollama_base_url
            self.llm_client = OpenAI(base_url=ollama_base_url, api_key="ollama")
            default_models = {
                "get_relevant_links_model": os.getenv("OLLAMA_GET_RELEVANT_LINK_MODEL", "llama3.2"),
                "generate_brochure_model": os.getenv("OLLAMA_GENERATE_BROCHURE_MODEL", "gpt-oss"),
            }

        # Assign models (use provided args if given, else defaults)
        self.get_relevant_links_model = get_link_relevant_model or default_models["get_relevant_links_model"]
        self.generate_brochure_model = generate_brochure_model or default_models["generate_brochure_model"]
    
    def get_relevant_links(self, website):
        """Get relevant links from the website using the language model."""
        link_system_prompt = """
        You are an expert web content analyzer. Your task is to identify and extract links from a given webpage that are most relevant to the main topic of the page. You are provided with a list of links found on a webpage. Provide only the URLs of the relevant links (such as About page, Company page, Careers/Jobs pages) to include in a brochure about the company without any additional commentary.
        You should return the links in a JSON array format as shown below:
        {
            "relevant_links": [
                {"type: "About page", "url": "https://example.com/about"},
                {"type: "Careers page", "url": "https://example.com/careers"}
            ]
        }
        """
        link_user_prompt = f"""
        Here is the URL of the webpage: {website.url}
        Your task is to analyze the links on this page and identify those that are most relevant to the main topic of the page for inclusion in a company brochure.
        Please return the relevant links in the specified JSON format.
        Do not include Terms of Service, Privacy Policy, email links, or any other unrelated links.
        Links:
        """
        link_user_prompt+= "\n".join(website.links)
        response = self.llm_client.chat.completions.create(
            model=self.get_relevant_links_model,
            messages=[
                {"role": "system", "content": link_system_prompt},
                {"role": "user", "content": link_user_prompt}
                ],
            response_format={"type": "json_object"}
        )
        result = response.choices[0].message.content
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            print("Error decoding JSON response:", result)
            return {"relevant_links": []}
    
    def generate_brochure(self, company_name, content, language="English"):
        """Generate a brochure for the company in the specified language."""
        
        brochure_system_prompt = """You are an expert marketing copywriter and brochure designer.

        Your task is to generate a **clean, professional, beautifully formatted Markdown brochure** using ONLY the information provided in the user message.

        ### Global Rules
        - Output must be **pure Markdown**, with **no code fences** and no HTML.
        - Use proper heading hierarchy: `#`, `##`, `###`.
        - Use bullet points for lists.
        - Use bold formatting to highlight key ideas.
        - Keep paragraphs short (2–4 lines maximum).
        - Maintain clean spacing (no double blank lines).
        - Never fabricate information beyond what’s reasonable or clearly implied.
        - If data is missing, make **neutral** assumptions (never overly positive).
        - The final result must look like a **real brochure** that a company would use.

        ### Safety & Accuracy
        - Do NOT invent statistical claims, certifications, or awards.
        - You may infer general company characteristics, but keep them realistic.
        - If something is unknown, phrase it generically (e.g., “The company focuses on delivering high-quality solutions.”).

        Your output should always look polished, structured, and ready to present to a customer.
        """
        

        
        brochure_user_prompt = f"""
        You are to create a brochure for {company_name}.
        Using the following webpage content and relevant links, create a compelling brochure for the company.
        Ensure the brochure is well-structured and highlights the company's strengths, values, and offerings.
        Use this information to build a short brochure of the company in {language} in beautiful markdown format without code blocks.
        
        ### REQUIRED MARKDOWN STYLE
        - Use clear headings (#, ##, ###)
        - Use bullet points
        - Use callout blocks (note, tip) when useful
        - Use bold for key items
        - Use tables for specs, data, or features
        - Start with a visually appealing header
        - No raw HTML
        - No inconsistent spacing
        - Keep formatting compact and professional

        ### REQUIRED STRUCTURE
        # {company_name}

        ## 📌 Overview
        Short description of the company.

        ## 🌐 Website
        `<URL>`

        ## ⭐ Key Strengths
        - ...
        - ...

        ## 🧩 Products / Services
        ### Product/Service Name
        Short description.

        ### Product/Service Name
        Short description.

        ## ⚙️ Technology / Innovation
        - ...

        ## 🤝 Contact & Social Links
        - Website
        - GitHub (if any)
        - Twitter (if any)
        - LinkedIn (if any)

        ---

        Always output **pure Markdown only**.
        """
        brochure_user_prompt += content[:5000]
        
        stream = self.llm_client.chat.completions.create(
            model=self.generate_brochure_model,
            messages=[
                {"role": "system", "content": brochure_system_prompt},
                {"role": "user", "content": brochure_user_prompt}
                ],
            stream=True
        )
        response_text = ""
        for chunk in stream:
            if hasattr(chunk.choices[0].delta, "content"):
                token = chunk.choices[0].delta.content or ""
                response_text += token
                print(token, end="", flush=True)
        print("\n\n")
        return response_text

            
        

    