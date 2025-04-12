# 🛡️ Offensive Comment Detection with LLaMA 3.1 (Ollama)

This Python CLI tool analyzes user comments for offensive content using the LLaMA 3.1 language model via [Ollama](https://ollama.com). It leverages both local profanity filters and large language model reasoning to identify various types of offensive content.

## 🚀 Features

- ✅ Analyze comments using LLaMA 3.1 (via Ollama API)
- 🧼 Pre-filter using `better_profanity` for quick profanity detection
- 📈 Visualize offense type distribution (bar chart or pie chart)
- 🧪 Filter results to show only offensive comments
- 📦 Supports JSON and CSV input files
- 🖥️ Simple CLI interface for flexibility
- 💾 Output results to a formatted JSON file with explanations
- 📊 Save offense breakdown chart as PNG

---

## 📦 Requirements

Install the dependencies via pip:
```
pip install pandas requests better_profanity matplotlib
```
## Also, make sure Ollama is installed and running with LLaMA 3.1 pulled:

```
ollama run llama3.1
```

## 📁 Input Format
Input can be a .json or .csv file with the following structure:

```
[
  {
    "comment_id": 1,
    "username": "john_doe",
    "comment_text": "You're such a loser, nobody likes you."
  },
  ...
]
```

Or CSV format with headers:

```
comment_id,username,comment_text
1,john_doe,You're such a loser, nobody likes you.

```
## 🛠️ How It Works

# 1. Pre-filtering: Comments are first checked using better_profanity.

# 2. LLaMA 3.1 Analysis: If no profanity is detected, LLaMA 3.1 is prompted via Ollama with a JSON-only response format.

# 3. Classification Output:

 - is_offensive: true / false

 - offense_type: one of ["hate speech", "toxicity", "profanity", "harassment", "none"]

 - explanation: short explanation of the decision

## 📈 Output
# 1. analyzed_comments.json: JSON file with original + classified results

# 2. offense_distribution.png: Chart image showing the offense distribution

# 3. CLI prints:

 - Total offensive comments

 - Breakdown of offense types

 - Top 5 offensive examples