from website import Website
from llmclient import LLMClient
from dotenv import load_dotenv

class BrochureGenerator:
    """ Main class to generate brochures from website content."""
    
    def __init__(self, company_name, url, language = "English") -> None:
        self.company_name = company_name
        self.url = url
        self.language = language
        self.website = Website(url, contents_limit=2000)
        self.llm_client = LLMClient()
            
    def generate(self):
        """ Generate the brochure by fetching relevant links and contents."""
        relevant_links = self.llm_client.get_relevant_links(self.website)
        content = self.website.get_contents()

        # Fetch contents from relevant links
        for link in relevant_links.get("relevant_links", []):
            linked_website = Website(link["url"], contents_limit=2000)
            content += linked_website.get_contents()
        return self.llm_client.generate_brochure( self.company_name, content, self.language)
    
def parse_args():
    import argparse
    parser = argparse.ArgumentParser(description="Generate a brochure for a company from its website.")
    parser.add_argument("company_name", type=str, help="The name of the company.")
    parser.add_argument("url", type=str, help="The URL of the company's website.")
    parser.add_argument("--language", type=str, default="English", help="The language for the brochure.")
    return parser.parse_args()
def main():
    args = parse_args()
    load_dotenv()
    generator = BrochureGenerator(args.company_name, args.url, args.language)
    brochure = generator.generate()
    with open(f"{args.company_name}_brochure.md", "w", encoding="utf-8") as f:
        f.write(brochure)
    print(f"Brochure for {args.company_name} generated and saved to {args.company_name}_brochure.md")

if __name__ == "__main__":
    main()