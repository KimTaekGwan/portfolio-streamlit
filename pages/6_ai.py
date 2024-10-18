import streamlit as st
import json
import openai

# Ensure that you have set your OpenAI API key appropriately
# You can set it via the openai.api_key variable, or set the OPENAI_API_KEY environment variable
# Example: openai.api_key = 'your-api-key'
# Do not include your API key directly in the code for security reasons


def load_products():
    """
    Load product data from a JSON file.

    Returns:
        products (list): List of product dictionaries.
    """
    with open("data/products.json", "r", encoding="utf-8") as f:
        products = json.load(f)
    return products


def initialize_session_state(products):
    """
    Initialize session state variables.

    Args:
        products (list): List of product dictionaries.
    """
    if "qa_history" not in st.session_state:
        st.session_state.qa_history = []
    if "recommendation_score" not in st.session_state:
        # Initialize recommendation scores for each product
        st.session_state.recommendation_score = {
            product["name"]: 0 for product in products
        }
    if "question_count" not in st.session_state:
        st.session_state.question_count = 0
    if "finished" not in st.session_state:
        st.session_state.finished = False


def evaluate_recommendation(qa_history, products):
    """
    Evaluate the recommendation scores for each product using OpenAI's API.

    Args:
        qa_history (list): List of dictionaries containing previous questions and answers.
        products (list): List of product dictionaries.
    """
    # Construct product descriptions
    product_descriptions = "\n".join(
        [
            f"Product Name: {p['name']}\nDescription: {p['description']}"
            for p in products
        ]
    )
    # Construct QA history
    qa_history_str = "\n".join(
        [f"Q: {qa['question']}\nA: {qa['answer']}" for qa in qa_history]
    )
    # Construct previous recommendation scores
    recommendation_scores_str = "\n".join(
        [
            f"{name}: {score}"
            for name, score in st.session_state.recommendation_score.items()
        ]
    )

    # Construct messages for OpenAI API
    messages = [
        {
            "role": "system",
            "content": (
                "You are an AI assistant that evaluates product recommendation scores based on user interactions. "
                "Analyze the user's answers and update the recommendation scores for each product accordingly. "
                "Provide the updated scores in JSON format without any additional explanation."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Products:\n{product_descriptions}\n\n"
                f"User's previous question-answer history:\n{qa_history_str}\n\n"
                f"Previous recommendation scores:\n{recommendation_scores_str}\n\n"
                "Based on the user's answers, update the recommendation scores for each product. "
                "Only provide the updated scores in JSON format, where keys are product names and values are the scores."
            ),
        },
    ]

    # Call the OpenAI API
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            max_tokens=500,
            temperature=0.5,
        )
        # Parse the response
        updated_scores = json.loads(response["choices"][0]["message"]["content"])

        # Update the recommendation scores
        for product_name, score in updated_scores.items():
            st.session_state.recommendation_score[product_name] = score
    except Exception as e:
        st.error(f"Error in evaluating recommendation: {e}")


def generate_qa(qa_history, products):
    """
    Generate the next question and answer options using OpenAI's API.

    Args:
        qa_history (list): List of dictionaries containing previous questions and answers.
        products (list): List of product dictionaries.

    Returns:
        question (str): The generated question.
        answers (list): List of answer options (minimum 2, maximum 5).
    """
    # Construct QA history
    if qa_history:
        qa_history_str = "\n".join(
            [f"Q: {qa['question']}\nA: {qa['answer']}" for qa in qa_history]
        )
    else:
        qa_history_str = "None"

    # Construct messages for OpenAI API
    messages = [
        {
            "role": "system",
            "content": (
                "You are an AI assistant that generates the next question and answer options for a product recommendation system. "
                "The questions should help narrow down the user's preferences. Provide the question and answers in JSON format."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Previous question-answer history:\n{qa_history_str}\n\n"
                "Generate the next question and 2 to 5 answer options to help recommend a product. "
                "Provide the output in the following JSON format:\n"
                '{\n  "question": "Your generated question",\n  "answers": ["Option 1", "Option 2", ..., "Option N"]\n}'
            ),
        },
    ]

    # Call the OpenAI API
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            max_tokens=500,
            temperature=0.7,
        )
        # Parse the response
        content = response["choices"][0]["message"]["content"]
        output = json.loads(content)
        question = output["question"]
        answers = output["answers"]
        return question, answers
    except Exception as e:
        st.error(f"Error in generating question and answers: {e}")
        return None, None


def display_qa_history():
    """
    Display the previous question-answer history.
    """
    if st.session_state.qa_history:
        st.write("**이전 질문-답변 기록:**")
        for idx, qa in enumerate(st.session_state.qa_history, 1):
            st.write(f"**질문 {idx}:** {qa['question']}")
            st.write(f"**답변:** {qa['answer']}")


def generate_final_recommendation(qa_history, products):
    """
    Generate the final recommendation using OpenAI's API.

    Args:
        qa_history (list): List of dictionaries containing previous questions and answers.
        products (list): List of product dictionaries.

    Returns:
        recommended_product_name (str): The name of the recommended product.
        reason (str): The reason for the recommendation.
    """
    # Get the product with the highest recommendation score
    recommended_product_name = max(
        st.session_state.recommendation_score,
        key=st.session_state.recommendation_score.get,
    )
    recommended_product = next(
        (p for p in products if p["name"] == recommended_product_name), None
    )

    if not recommended_product:
        st.error("Recommended product not found.")
        return None, None

    # Prepare the prompt
    product_description = f"Product Name: {recommended_product['name']}\nDescription: {recommended_product['description']}"
    qa_history_str = "\n".join(
        [f"Q: {qa['question']}\nA: {qa['answer']}" for qa in qa_history]
    )

    messages = [
        {
            "role": "system",
            "content": (
                "You are an AI assistant that provides a final product recommendation to the user, along with a personalized reason based on their previous answers. "
                "Provide the reason in JSON format without any additional explanation."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Recommended product:\n{product_description}\n\n"
                f"User's previous question-answer history:\n{qa_history_str}\n\n"
                "Provide a personalized recommendation reason to the user. "
                'Output in the following JSON format:\n{\n  "reason": "Your personalized reason for the recommendation"\n}'
            ),
        },
    ]

    # Call the OpenAI API
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            max_tokens=150,
            temperature=0.7,
        )
        # Parse the response
        content = response["choices"][0]["message"]["content"]
        output = json.loads(content)
        reason = output["reason"]
        return recommended_product_name, reason
    except Exception as e:
        st.error(f"Error in generating final recommendation: {e}")
        return None, None


def main():
    """
    Main function to run the Streamlit app.
    """
    st.title("상품 추천 시스템")

    # Load products
    products = load_products()

    # Initialize session state
    initialize_session_state(products)

    if st.session_state.finished:
        st.header("최종 추천 결과")
        # Generate final recommendation
        recommended_product_name, reason = generate_final_recommendation(
            st.session_state.qa_history, products
        )
        if recommended_product_name and reason:
            st.write(f"**추천 상품명:** {recommended_product_name}")
            st.write(f"**이유:** {reason}")
            # Display previous QA history
            display_qa_history()
    else:
        # Display previous QA history
        display_qa_history()

        if st.session_state.question_count >= 5:
            st.session_state.finished = True
            st.experimental_rerun()
        else:
            # Generate question and answers
            question, answers = generate_qa(st.session_state.qa_history, products)
            if question and answers:
                st.write(f"**질문 {st.session_state.question_count + 1}:** {question}")
                user_answer = st.radio(
                    "답변을 선택하세요:",
                    answers,
                    key=f"answer_{st.session_state.question_count}",
                )

                if st.button(
                    "답변 제출", key=f"submit_{st.session_state.question_count}"
                ):
                    # Save the answer
                    st.session_state.qa_history.append(
                        {"question": question, "answer": user_answer}
                    )
                    st.session_state.question_count += 1

                    # Evaluate recommendation
                    evaluate_recommendation(st.session_state.qa_history, products)

                    # Check if recommendation score exceeds threshold (e.g., 5)
                    if max(st.session_state.recommendation_score.values()) >= 5:
                        st.session_state.finished = True

                    # Rerun to update the UI
                    st.experimental_rerun()
            else:
                st.error("질문을 생성하는 데 실패했습니다.")


if __name__ == "__main__":
    main()
