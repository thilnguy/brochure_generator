from website import Website
from llmclient import LLMClient
from dotenv import load_dotenv

class BrochureGenerator:
    """ Main class to generate brochures from website content."""
    
    def __init__(self, company_name, url, language = "English", get_link_relevant_model=None, create_brochure_model=None) -> None:
        self.company_name = company_name
        self.url = url
        self.get_link_relevant_model = get_link_relevant_model
        self.create_brochure_model = create_brochure_model
        self.language = language
        self.website = Website(url, contents_limit=2000)
        
        self.llm_client = LLMClient(get_link_relevant_model, create_brochure_model)
            
    def generate(self):
        """ Generate the brochure by fetching relevant links and contents.
        """
        relevant_links = self.llm_client.get_relevant_links(self.website)
        content = self.website.get_contents()

        # Fetch contents from relevant links
        for link in relevant_links.get("relevant_links", []):
            if not link.get("url"):
                continue
            linked_website = Website(link["url"], contents_limit=2000)
            content += linked_website.get_contents()
        
        return self.llm_client.generate_brochure( self.company_name, content, self.language)
        