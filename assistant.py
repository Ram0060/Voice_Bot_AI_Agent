import openai
import time
from app.config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY
ASSISTANT_ID = "asst_zmYBdM85QqbnTKsXYTFqXYXi"

def get_assistant_response(user_input: str, thread_id: str) -> str:
    try:
        print(f"💬 Using existing thread: {thread_id}")

        openai.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_input
        )

        run = openai.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID
        )

        print("⏳ Waiting for assistant to complete...")
        while True:
            run_status = openai.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
            if run_status.status == "completed":
                print("✅ Assistant run completed.")
                break
            elif run_status.status == "failed":
                error_info = run_status.last_error
                print("❌ Assistant run failed.")
                if error_info:
                    print(f"🔍 Reason: {error_info.code}")
                    print(f"📄 Message: {error_info.message}")
                return "[Error getting assistant response]"
            time.sleep(1)

        messages = openai.beta.threads.messages.list(thread_id=thread_id)
        for msg in reversed(messages.data):
            if msg.role == "assistant" and msg.content and msg.content[0].type == "text":
                response_text = msg.content[0].text.value.strip()
                print("🤖 Assistant replied:", response_text)
                return response_text

        print("⚠️ No assistant message found.")
        return "[Assistant did not return a valid response]"

    except Exception as e:
        print(f"[ERROR] Assistant failed: {e}")
        return "[Error getting assistant response]"
