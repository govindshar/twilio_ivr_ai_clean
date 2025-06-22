from transformers import pipeline
qa_pipeline = pipeline("text-generation", model="sshleifer/tiny-gpt2")

def get_response(query):
    return qa_pipeline(query, max_length=50)[0]['generated_text']