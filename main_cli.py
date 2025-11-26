   
from dotenv import load_dotenv
from brochure_generator import BrochureGenerator

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
    
    generator = BrochureGenerator(args.company_name, args.url, args.language, None, None)
    brochure = generator.generate()
    
    # Save brochure to a markdown file
    with open(f"{args.company_name}_brochure.md", "w", encoding="utf-8") as f:
        f.write(brochure)
    print(f"Brochure for {args.company_name} generated and saved to {args.company_name}_brochure.md")

if __name__ == "__main__":
    main()