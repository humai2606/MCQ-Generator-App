import os
import json
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("GROQ_API_KEY not found. Please check your .env file.")
    st.stop()

client = Groq(api_key=api_key)

st.set_page_config(
    page_title="MCQ Generator",
    page_icon="📝",
    layout="centered"
)

st.title("MCQ Generator App")
st.write("Generate multiple-choice questions using AI.")

topic = st.text_input("Enter Topic")

num_questions = st.number_input(
    "Number of Questions",
    min_value=1,
    max_value=20,
    value=5
)

difficulty = st.selectbox(
    "Select Difficulty",
    ["Easy", "Medium", "Hard"]
)

generate = st.button("Generate MCQs")

if generate:

    if not topic:
        st.warning("Please enter a topic.")
        st.stop()

    prompt = f"""
Generate {num_questions} multiple-choice questions about "{topic}".

Difficulty: {difficulty}

For each question provide:
- Question
- Four options: A, B, C, D
- Correct answer
- Short explanation

Return ONLY valid JSON in this format:

[
  {{
    "question": "Question text",
    "options": {{
      "A": "Option A",
      "B": "Option B",
      "C": "Option C",
      "D": "Option D"
    }},
    "answer": "B",
    "explanation": "Short explanation"
  }}
]
"""

    with st.spinner("Generating MCQs..."):

        try:
            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert MCQ generator."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7
            )

            result = response.choices[0].message.content

            result = result.replace("```json", "").replace("```", "").strip()

            mcqs = json.loads(result)

            st.success("MCQs generated successfully!")

            for i, mcq in enumerate(mcqs, start=1):

                st.subheader(f"Question {i}")

                st.write(mcq["question"])

                for key, option in mcq["options"].items():
                    st.write(f"**{key}.** {option}")

                st.info(
                    f"Correct Answer: {mcq['answer']}. "
                    f"{mcq['options'][mcq['answer']]}"
                )

                st.write(
                    f"**Explanation:** {mcq['explanation']}"
                )

                st.divider()

        except json.JSONDecodeError:
            st.error("Unable to process the generated questions.")

        except Exception as e:
            st.error(f"Error: {e}")