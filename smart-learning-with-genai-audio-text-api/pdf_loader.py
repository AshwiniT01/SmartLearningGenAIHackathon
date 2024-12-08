import boto3
import PyPDF2
import logging

class S3PDFLoader:
    def __init__(self, bucket_name, pdf_key):
        """
        Initializes the loader with the S3 bucket name and PDF file key.
        
        :param bucket_name: Name of the S3 bucket.
        :param pdf_key: Key of the PDF file in the S3 bucket.
        """
        self.bucket_name = bucket_name
        self.pdf_key = pdf_key
        self.s3_client = boto3.client("s3")
        self.logger = logging.getLogger(__name__)

    def download_pdf(self, local_path):
        """
        Downloads the PDF file from S3 to a local path.
        
        :param local_path: Path to save the downloaded PDF file.
        :return: None
        """
        try:
            self.s3_client.download_file(self.bucket_name, self.pdf_key, local_path)
            self.logger.info(f"Downloaded PDF from S3: {self.pdf_key}")
        except Exception as e:
            self.logger.error(f"Error downloading PDF from S3: {str(e)}")
            raise

    def load_pdf_content(self, local_path):
        """
        Loads the content of the PDF file and extracts text.
        
        :param local_path: Local path of the downloaded PDF file.
        :return: Extracted text with tabs replaced by spaces.
        """
        try:
            with open(local_path, "rb") as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()

                # Replace tabs with spaces
                text = text.replace('\t', ' ')
                return text
        except Exception as e:
            self.logger.error(f"Error reading PDF file: {str(e)}")
            raise

    def get_text_from_pdf(self, local_path="/tmp/temp_pdf.pdf"):
        """
        High-level method to download the PDF and extract text.
        
        :param local_path: Temporary local path for the downloaded PDF.
        :return: Extracted and processed text.
        """
        self.download_pdf(local_path)
        return self.load_pdf_content(local_path)
