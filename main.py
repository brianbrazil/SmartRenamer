from openai import OpenAI
import base64
import magic
import mimetypes
import pdb
import sys
import os
from dotenv import load_dotenv
from pdf2image import convert_from_path
from io import BytesIO

class Namifier:
    def __init__(self, file_path):
        load_dotenv()
        self.file_path = file_path
        self.mime = magic.from_file(file_path, mime=True)

    def get_image_from_pdf(self):
        # images = convert_from_path(self.file_path, single_file=True) # all pages
        images = convert_from_path(self.file_path, first_page=1, last_page=1) # first page only
        if images:
            buffered = BytesIO()
            images[0].save(buffered, format="JPEG")
            img_bytes = buffered.getvalue()
            return base64.b64encode(img_bytes).decode('utf-8')
        return None

    def encode_image(self):
      with open(self.file_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

    def generate_title_for_image(self, image):
        completion = self.client.chat.completions.create(
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

    def generate_title_for_text(self, text):
        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [{
                        "type": 'text',
                        "text": f"Suggest a concise title for the attached text document. Return only the title. Include dates (with month precision) only if it is prominent in the document; place the dates in parentheses. Format it as a legal macos filename. Prefer spaces over underscores. Include '-' when necessary. This is the text document: {text}",
                    }]
                },

            ]
        )
        return completion.choices[0].message.content

    @property
    def client(self):
        return OpenAI(api_key = os.getenv("OPENAI_API_KEY"))

    @property
    def title(self):
        if self.mime == 'application/pdf':
            image = self.get_image_from_pdf()
            return self.generate_title_for_image(image)
        elif self.mime.startswith('image'):
            image = self.encode_image()
            return self.generate_title_for_image(image)
        elif self.mime == 'text/plain':
            with open(file_path, 'r') as f:
                text = f.read()
            return self.generate_title_for_text(text)
        else:
            raise ValueError(f"Unsupported file type: {self.mime}")

    @property
    def extension(self):
        return mimetypes.guess_extension(self.mime)

if __name__ == "__main__":
    file_path = sys.argv[1]
    namifier = Namifier(file_path)
    print(f"{namifier.title}{namifier.extension}")
