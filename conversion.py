import openai
import streamlit as st
import os
from openai import OpenAI

client =OpenAI(api_key = os.environ['OPENAI_API_KEY'])

#Formal
def formal_translator(prompt):
  system_prompt = """
  Transform a informal or casual sentences into 3 professional language suitable for workplace communication.

  - Focus on maintaining professionalism and clarity in the revised sentences.
  - Avoid using slang, overly casual language, or ambiguous phrases.
  - Ensure that the core message of the original sentence is preserved.
  - Ensure that any sensitive or culturally specific terms are treated with respect and professionalism.
  - Maintain the formality level consistent with typical workplace communication guidelines.
  
  # Steps
  1. Analyze the provided sentence to understand its core message.
  2. Identify any informal or casual language that needs to be transformed.
  3. Rewrite the sentence using professional language, ensuring clarity and appropriateness for a workplace setting.
  4. Review the transformed sentence to ensure the core message is intact, simple and professional.
  5. Convert negative sentences to positive messages

  # Output Format
  - The output should be 3 single, professionally rewritten sentences each separated by an empty line.
  - Maintain clarity and conciseness in the revised sentence.
  """

  response = client.chat.completions.create(
      model = "gpt-4o-mini",
      messages = [
          {"role": "system", "content": system_prompt},
          {"role": "user", "content": "Give this to John?"},
          {"role": "assistant", "content": (
              "Could you please kindly help me to hand the documents to John?\n\n"
              "Please pass this document to John.\n\n"
              "Please hand this over to John."
          )},
          {"role": "user", "content": "I need that report, like, yesterday!"},
          {"role": "assistant", "content": (
              "Could you please prioritize and send me the report as soon as possible?\n\n"
              "I would greatly appreciate it if you could provide that report at your earliest convenience.\n\n"
              "I would appreciate it if you could expedite the delivery of that report. Thank you for your prompt attention to this matter."
          )},
          {"role": "user", "content": "That idea sounds kinda off."},
          {"role": "assistant", "content": (
              "I have some reservations about that idea, but we can have a try on it.\n\n"
              "It may be beneficial to reconsider that idea for improved alignment with our objectives.\n\n"
              "I believe we should explore alternative approaches, as this idea may not fully meet our expectations.")},
          {"role": "user", "content": prompt}
      ],
      temperature = 1.3,
      max_tokens = 1000,
  )
  return response.choices[0].message.content


prompt = st.text_input("Enter a sentence")
if st.button("Translate"):
    formal = formal_translator(prompt)
    st.write(formal)