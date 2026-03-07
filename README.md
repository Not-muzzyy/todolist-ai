# 🎓 StudentFlow AI (MIT)

A fully Python + Streamlit AI planner for students in India.

## What changed
- ✅ Built entirely in **Python** using **Streamlit** (no separate JS/CSS/HTML frontend files required).
- ✅ AI integration is **Groq API only**.
- ✅ Includes advanced student-focused planning for common India-specific challenges:
  - exam anxiety
  - backlog overload
  - language confidence
  - commute / internet issues
  - family + financial pressure
- ✅ Open source under the **MIT License**.

## Features
- Smart task manager with priority and due-date tracking
- Stress-risk scoring for each task
- Progress dashboard with completion analytics
- AI mentor chat (Groq) that returns:
  1. key issue
  2. 7-day plan
  3. today focus (max 3 tasks)
  4. motivation line
- Student support resources for India

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export GROQ_API_KEY="your_groq_api_key"
streamlit run app.py
```

Then open the local Streamlit URL (usually `http://localhost:8501`).

## Project structure

```text
todolist-ai/
├── app.py
├── requirements.txt
├── LICENSE
└── README.md
```

## License

This project is licensed under the MIT License. See `LICENSE`.

## Contributors
Special thanks to all contributors who helped improve this project.

