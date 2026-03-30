# 🤖 Kilo AI Model Selector Guide

The Manver AI Interviewer is optimized for the **Kilo.ai Gateway**. This guide will help you choose the best model for your interview.

## ⭐ Kilo AI Free Tier Models
These models are 100% free and don't require an active subscription to start.

| Model ID | Best For | Speed |
| :--- | :--- | :--- |
| **`kilo-auto/free`** | General Purpose (Auto-routes to the best free model) | Fast |
| **`minimax/minimax-m2.5:free`** | High-performance technical questioning | Very Fast |
| **`z-ai/glm-5:free`** | Large context, deep reasoning | Moderate |
| **`corethink:free`** | Concise, fast analysis | Extremely Fast |

## 🚀 Recommended Approach
- **Resume Analysis**: Use `z-ai/glm-5:free` (if available) for its deep reasoning, or `kilo-auto/free` for reliability.
- **Question Generation**: Use `minimax/minimax-m2.5:free` for fast, clever technical questions.
- **Answer Evaluation**: Use `corethink:free` for rapid, brief feedback.

## 🔑 AI Gateway Setup
1.  **Anonymous Mode**: If you don't have a Kilo API Key, the app will try to connect anonymously.
2.  **Authenticated Mode**: For higher rate limits, add your `VITE_KILO_API_KEY` to the `.env` file. You can get one at [kilo.ai](https://kilo.ai).

## 💡 Fallback Logic
The app contains an internal fallback list. If a specific model is busy or rate-limited, it will automatically cycle through the other available free models to ensure your interview isn't interrupted.
