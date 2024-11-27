from openai import OpenAI
import base64
import pdb
import sys
import os
from dotenv import load_dotenv
from pdf2image import convert_from_path
from io import BytesIO

def get_image_from_pdf(pdf_path):
    # images = convert_from_path(pdf_path, single_file=True) # all pages
    images = convert_from_path(pdf_path, first_page=1, last_page=1) # first page only
    if images:
        buffered = BytesIO()
        images[0].save(buffered, format="JPEG")
        img_bytes = buffered.getvalue()
        return base64.b64encode(img_bytes).decode('utf-8')
    return None

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

def generate_title(image):
    client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [{
                    "type": 'text',
                    "text": "Suggest a concise title for this image. Return only the title. Include dates (with month precision) if it is prominent in the document; place the dates in parentheses. Format it as a legal macos filename. Prefer spaces over underscores. Include '-' when necessary.",
                }, {
                    "type": 'image_url',
                    "image_url": { "url": f"data:image/jpeg;base64,{image}" }
                }]
            },

        ]
    )
    return completion.choices[0].message.content

def main(pdf_path):
    """Main function to extract text from a PDF and generate a title."""
    load_dotenv()
    image = get_image_from_pdf(pdf_path)
    title = generate_title(image)
    print(title, end='')

if __name__ == "__main__":
    pdf_path = sys.argv[1]
    main(pdf_path)