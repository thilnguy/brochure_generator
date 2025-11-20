import os
from openai import OpenAI
import json


class LLMClient:
    """A client to interact with a language model API."""
    
    def __init__(self):
        USE_API = os.getenv("USE_API", "False").lower() in ("true", "1", "t")
        if USE_API:
            API_GET_RELEVANT_LINK_MODEL = os.getenv("API_GET_RELEVANT_LINK_MODEL", "gpt-4_mini")
            API_GENERATE_BROCHURE_MODEL = os.getenv("API_GENERATE_BROCHURE_MODEL", "gpt-4_mini")
                        
            self.llm_client = OpenAI()
            self.get_relevant_links_model = API_GET_RELEVANT_LINK_MODEL
            self.generate_brochure_model = API_GENERATE_BROCHURE_MODEL
        else:
            OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
            self.ollama_base_url = OLLAMA_BASE_URL
            self.llm_client = OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")
            self.get_relevant_links_model = os.getenv("OLLAMA_GET_RELEVANT_LINK_MODEL", "llama3.2")
            self.generate_brochure_model = os.getenv("OLLAMA_GENERATE_BROCHURE_MODEL", "gpt-oss")
    
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
        
        brochure_system_prompt = """
        You are a skilled brochure writer. Your task is to create a compelling brochure for a company based on the provided webpage content and relevant links. Use the information to highlight the company's strengths, values, and offerings in an engaging manner.
        The brochure should be well-structured, informative, and persuasive, aiming to attract potential customers or clients.
        Respond in markdown format without code blocks.
        Include sections such as Introduction, About Us, Services/Products, Careers, and Contact Information where applicable.
        """
        
        brochure_user_prompt = f"""
        You are to create a brochure for {company_name}.
        Using the following webpage content and relevant links, create a compelling brochure for the company.
        Ensure the brochure is well-structured and highlights the company's strengths, values, and offerings.
        Use this information to build a short brochure of the company in {language} in beautiful markdown format without code blocks.
        """
        brochure_user_prompt += content[:5000]
        
        response = self.llm_client.chat.completions.create(
            model=self.generate_brochure_model,
            messages=[
                {"role": "system", "content": brochure_system_prompt},
                {"role": "user", "content": brochure_user_prompt}
                ]
        )
        return response.choices[0].message.content

            
        

    