import os
import streamlit as st
from openai import OpenAI
#from google.colab import userdata
#from IPython.display import Image

#client = OpenAI(api_key = os.environ['OPENAI_API_KEY'])
client = OpenAI(api_key = st.secrets['OPENAI_API_KEY']) #for streamlit deployment
#Story
def story_gen(prompt):
  system_prompt = """
  You are a world-class romance book author. You are a hopeless romantic wife and mother with a loving husband and kids.
  You get inspiration from your life, and you are also emotional and dramatic.
  """

  response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
      {'role': 'system', 'content': system_prompt},
      {'role':'user','content':prompt}
    ],
    temperature = 1.2,
    max_tokens = 1500
  )
  return response.choices[0].message.content

#cover
def art_gen(prompt):
  response = client.images.generate(
      model = 'dall-e-2',
      prompt = prompt,
      size = '1024x1024',
      n = 1
  )
  return response.data[0].url

#cover prompt design
def design_gen(prompt):
  system_prompt = """
  You will be given a short story. Generate a prompt for a cover art that s suitable for the story.
  The prompt  is for dall-e-2.
  """
  response = client.chat.completions.create(
      model = 'gpt-4o-mini',
      messages = [
          {'role':'system','content':system_prompt},
          {'role':'user','content':prompt}
      ]
  )
  return response.choices[0].message.content

prompt = st.text_input("Enter a prompt")
if st.button("Generate"):
  story = story_gen(prompt)
  design = design_gen(story)
  art = art_gen(design)

  st.caption(design)
  st.divider()
  st.write(story)
  st.divider()
  st.image(art)