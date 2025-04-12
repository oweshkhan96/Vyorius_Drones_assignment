import argparse
import pandas as pd
import requests
import json
import time
import matplotlib.pyplot as plt
from better_profanity import profanity

profanity.load_censor_words()

def load_comments(file_path):
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    elif file_path.endswith('.json'):
        df = pd.read_json(file_path)
    else:
        raise ValueError("Unsupported file format. Use CSV or JSON.")
    
    print(f"\n✅ Total Comments Loaded: {len(df)}")
    print("\n🔍 Sample Preview:")
    print(df.head(3))
    return df

def clean_output(raw_output):
    if raw_output.startswith("```"):
        lines = raw_output.splitlines()
        if len(lines) >= 3:
            raw_output = "\n".join(lines[1:-1]).strip()
    return raw_output

def analyze_comment(comment_text):
    prompt = f"""
You are a content moderation assistant. Analyze the following user comment and return a JSON object with:
- is_offensive: true or false
- offense_type: one of ["hate speech", "toxicity", "profanity", "harassment", "none"]
- explanation: a brief explanation for the classification

Comment: "{comment_text}"

Respond only with the JSON object.
"""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama3.1:latest", "prompt": prompt, "stream": False},
            timeout=30
        )
        data = response.json()
        if "response" not in data:
            raise ValueError("Missing 'response' key in API reply")
        
        output_text = data["response"].strip()
        cleaned_output = clean_output(output_text)
        try:
            analysis = json.loads(cleaned_output)
        except Exception as parse_error:
            print(f"⚠️ Could not parse output as JSON. Raw output: {cleaned_output}")
            analysis = {"is_offensive": False, "offense_type": "none", "explanation": "Parsing error"}
    except Exception as e:
        print(f"⚠️ Error analyzing comment: {e}")
        analysis = {"is_offensive": False, "offense_type": "none", "explanation": "API error"}
    
    return analysis

def analyze_all_comments(df):
    df["is_offensive"] = False
    df["offense_type"] = "none"
    df["explanation"] = ""
    
    for idx, row in df.iterrows():
        comment_text = row['comment_text']
        print(f"🔎 Analyzing comment {row['comment_id']} by {row['username']}")
        
        # Pre-filter: check if comment contains profanity using better_profanity
        if profanity.contains_profanity(comment_text):
            print("  🛑 Pre-filter detected profanity.")
            df.at[idx, 'is_offensive'] = True
            df.at[idx, 'offense_type'] = "profanity"
            df.at[idx, 'explanation'] = "Pre-filter detected profanity in comment."
        else:
            analysis = analyze_comment(comment_text)
            df.at[idx, 'is_offensive'] = analysis.get('is_offensive', False)
            df.at[idx, 'offense_type'] = analysis.get('offense_type', "none")
            df.at[idx, 'explanation'] = analysis.get('explanation', "No explanation provided")
        time.sleep(1)
    
    return df

def generate_report(df, only_offensive=False, chart_type="bar"):
    if only_offensive:
        df = df[df['is_offensive'] == True]
    
    offensive_df = df[df['is_offensive'] == True]
    
    print(f"\n🚨 Number of Offensive Comments: {len(offensive_df)}")
    
    print("\n📊 Offense Type Breakdown:")
    if not offensive_df.empty:
        breakdown = offensive_df['offense_type'].value_counts()
        print(breakdown)
    else:
        print("No offensive comments found.")
        breakdown = None

    print("\n🔥 Top 5 Offensive Comments:")
    if not offensive_df.empty:
        print(offensive_df[['username', 'comment_text', 'offense_type', 'explanation']].head(5))
    else:
        print("No offensive comments to display.")
    
    output_file = "analyzed_comments.json"
    df.to_json(output_file, orient="records", indent=2)
    print(f"\n✅ Results saved to '{output_file}'")
    
    if breakdown is not None:
        plt.figure(figsize=(8, 6))
        if chart_type.lower() == "pie":
            breakdown.plot.pie(autopct='%1.1f%%', startangle=90, counterclock=False)
            plt.ylabel('')
            plt.title("Offense Type Distribution (Pie Chart)")
        else:
            breakdown.plot.bar(color='skyblue')
            plt.xlabel("Offense Type")
            plt.ylabel("Count")
            plt.title("Offense Type Distribution (Bar Chart)")
        plt.tight_layout()
        chart_file = "offense_distribution.png"
        plt.savefig(chart_file)
        plt.show()
        print(f"✅ Chart saved to '{chart_file}'")

def parse_args():
    parser = argparse.ArgumentParser(description="Comment Moderation using LLaMA 3.1 via Ollama")
    parser.add_argument("--input-file", type=str, default="comments.json",
                        help="Path to the input CSV/JSON file with comments")
    parser.add_argument("--only-offensive", action="store_true",
                        help="Filter output to only offensive comments")
    parser.add_argument("--chart-type", type=str, choices=["bar", "pie"], default="bar",
                        help="Type of chart to display for offense distribution")
    return parser.parse_args()

def main():
    args = parse_args()
    df = load_comments(args.input_file)
    analyzed_df = analyze_all_comments(df)
    generate_report(analyzed_df, only_offensive=args.only_offensive, chart_type=args.chart_type)

if __name__ == "__main__":
    main()
