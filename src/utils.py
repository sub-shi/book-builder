import time
from google.api_core.exceptions import ResourceExhausted


def cached_generate(model, prompt, max_retries=5):
    retry = 0

    while retry < max_retries:
        try:
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0,
                    "top_p": 1,
                    "top_k": 1
                }
            )

            return response.text if response and response.text else ""

        except ResourceExhausted as e:
            retry += 1

            # Extract wait time if available
            wait_time = 60 * retry

            print(f"Rate limit hit. Retry {retry}/{max_retries} in {wait_time}s...")
            time.sleep(wait_time)

            # If daily quota exceeded → STOP
            if "per day" in str(e).lower():
                print("Daily quota exhausted. Please resume later.")
                raise e

        except Exception as e:
            retry += 1
            wait_time = 30 * retry
            print(f"Error: {e}. Retrying in {wait_time}s...")
            time.sleep(wait_time)

    print("Max retries reached. Skipping...")
    return ""