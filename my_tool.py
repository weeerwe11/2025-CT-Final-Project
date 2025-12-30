import random
from pathlib import Path
import re
from ollama import Client

# --------------------
# Ollama 設定
# --------------------

api_key = "YOUR_API_KEY"
if not api_key:
    raise ValueError("請先設定 API_KEY")

client = Client(
    host="https://api-gateway.netdb.csie.ncku.edu.tw",
    headers={"Authorization": f"Bearer {api_key}"}
)

MODEL_NAME = "gemma3:4b"


# --------------------
# 題庫讀取
# --------------------

def load_questions_from_txt(path: Path):
    content = path.read_text(encoding="utf-8").strip()
    blocks = re.split(r"\n\s*\n", content)

    questions = []
    for block in blocks:
        lines = [l.strip() for l in block.splitlines() if l.strip()]
        if len(lines) < 6:
            continue

        sentence = lines[0]
        options = {}
        answer = None

        for line in lines[1:]:
            if line[:2] in {"A.", "B.", "C.", "D."}:
                options[line[0]] = line[3:].strip()
            elif line.startswith("Answer:"):
                answer = line.split(":", 1)[1].strip()

        if len(options) == 4 and answer in options:
            questions.append({
                "sentence": sentence,
                "options": options,
                "answer": answer
            })

    return questions


# --------------------
# Tools
# --------------------

class Tools:
    def __init__(self):
        self.question_file = Path(__file__).parent / "question.txt"
        if not self.question_file.exists():
            raise FileNotFoundError("question.txt not found")

        self.question_bank = load_questions_from_txt(self.question_file)
        self.current_question = None  # 題庫狀態

    # --------------------
    # LLM 呼叫
    # --------------------

    def _chat(self, prompt: str) -> str:
        response = client.chat(
            MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            stream=False
        )
        return response["message"]["content"].strip()

    # --------------------
    # 抽取單字
    # --------------------

    def extract_word(self, text: str) -> str:
        matches = re.findall(r"[A-Za-z][A-Za-z\- ]{1,30}", text)
        return matches[-1].strip() if matches else ""

    def extract_sentence(self, text: str) -> str:
        matches = re.findall(r"[A-Z][^.!?]*[.!?]", text)
        return matches[0].strip() if matches else ""

    # --------------------
    # Tool 1：Grammar
    # --------------------

    def grammar_and_spell_check(self, sentence: str) -> str:
        prompt = f"""
        Improve the following English sentence.

        Sentence:
        "{sentence}"

        Rules:
        - Correct grammar and spelling
        - Sound natural
        - Return ONLY the corrected sentence
        """
        return self._chat(prompt)

    # --------------------
    # Tool 2：Example
    # --------------------

    def generate_example(self, word_or_phrase: str) -> str:
        prompt = f"""
        Create ONE natural English sentence using:
        "{word_or_phrase}"
        Return ONLY the sentence.
        """
        return "Example: " + self._chat(prompt)

    # --------------------
    # Tool 3：題庫出題
    # --------------------

    def generate_practice(self) -> str:
        if not self.question_bank:
            return "❌ Question bank empty"

        q = random.choice(self.question_bank)
        while self.current_question == q and len(self.question_bank) > 1:
            q = random.choice(self.question_bank)

        self.current_question = q

        lines = [q["sentence"]]
        for k, v in q["options"].items():
            lines.append(f"{k}. {v}")

        return "\n".join(lines)

    # --------------------
    # Tool 4：Explain
    # --------------------

    def generate_explain(self, word_or_phrase: str) -> str:
        prompt = f"""
        Explain the meaning of:
        "{word_or_phrase}"

        Rules:
        - Start directly with the explanation
        - Easy English
        - 2–3 short sentences
        - No greetings
        - No Chinese
        """
        return self._chat(prompt)

    # --------------------
    # Router
    # --------------------

    def run(self, input_text: str) -> str:
        text = input_text.strip()
        upper = text.upper()

        # 【作答模式】A/B/C/D
        if upper in {"A", "B", "C", "D"} and self.current_question:
            correct = self.current_question["answer"]
            self.current_question = None

            if upper == correct:
                return "✅ Correct!"
            else:
                return f"❌ Wrong. Correct answer: {correct}"

        # 【題庫指令】不走 LLM
        if any(k in text.lower() for k in ["題"]):
            return self.generate_practice()

        # --------------------
        # LLM
        # --------------------

        router_prompt = f"""
        Choose ONE tool:

        - grammar_and_spell_check
        - generate_example
        - generate_explain

        User input:
        "{input_text}"

        Output ONLY the tool name.
        """
        tool_name = self._chat(router_prompt)

        if "grammar" in tool_name:
            sentence = self.extract_sentence(input_text)
            return self.grammar_and_spell_check(sentence)

        word = self.extract_word(input_text)
        if not word:
            return "❌ Please provide an English word or sentence."

        if "explain" in tool_name:
            return self.generate_explain(word)
        else:
            return self.generate_example(word)


# --------------------
# main
# --------------------

if __name__ == "__main__":
    tool = Tools()
    print("📘 LanguageTool (type 'exit' to quit)")
    print("-" * 40)

    while True:
        try:
            prompt = "Your answer: " if tool.current_question else ">>> "
            user_input = input(prompt).strip()
            if user_input.lower() in {"exit", "quit", "q"}:
                print("👋 Bye")
                break

            print("\n" + tool.run(user_input))
            print("-" * 40)

        except KeyboardInterrupt:
            print("\n👋 Bye")
            break



