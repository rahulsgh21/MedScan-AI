import os
import sys
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv

# Add the project root to the python path so we can import 'app'
sys.path.append(str(Path(__file__).parent.parent))

# Load Env
load_dotenv()
# Langchain Google GenAI looks for GOOGLE_API_KEY
if "GEMINI_API_KEY" in os.environ and "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]

from app.services.rag_engine import get_rag_engine
from app.services.llm_client import get_llm_client
from datasets import Dataset

from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings

def run_evaluation():
    print("Initiating RAGAS Evaluation Framework...")
    
    rag_engine = get_rag_engine()
    llm_client = get_llm_client()
    
    # 1. Configure Gemini as the Impartial Judge
    print("Configuring Gemini-2.0-Flash as the Judge...")
    evaluator_llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
    evaluator_embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    
    # 2. The Medical Ground Truth Dataset
    test_cases = [
        {
            "user_input": "What does a high troponin level indicate?",
            "reference": "High troponin indicates damage to the heart muscle, highly suggestive of a myocardial infarction or acute coronary syndrome."
        }
    ]
    
    data = {
        "user_input": [],
        "response": [],
        "retrieved_contexts": [],
        "reference": []
    }
    
    print("\n--- Simulating RAG Pipeline ---")
    for idx, test in enumerate(test_cases, 1):
        query = test["user_input"]
        print(f"\n[Test {idx}] Query: {query}")
        
        # Retrieval
        results = rag_engine.hybrid_search(query, top_k=2)
        contexts = [res["content"] for res in results]
        
        # Generation
        prompt = (
            f"Using the following medical context, strictly answer the patient's question concisely. "
            f"Do not hallucinate.\n\nContext:\n{contexts}\n\nQuestion: {query}"
        )
        response = llm_client.generate(prompt=prompt)
        
        data["user_input"].append(query)
        data["response"].append(response)
        data["retrieved_contexts"].append(contexts)
        data["reference"].append(test["reference"])
        
    dataset = Dataset.from_dict(data)
    
    print("\n--- Running RAGAS Evaluation Metrics ---")
    print("Metrics: Faithfulness, Answer Relevancy, Context Precision, Context Recall")
    
    from ragas.run_config import RunConfig
    
    result = evaluate(
        dataset=dataset,
        metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
        llm=evaluator_llm,
        embeddings=evaluator_embeddings,
        run_config=RunConfig(max_workers=2)
    )
    
    # Save the output
    df = result.to_pandas()
    output_path = Path(__file__).parent.parent / "ragas_eval_results.csv"
    df.to_csv(output_path, index=False)
    
    print("\n\n" + "="*40 + "\n")
    print("RAGAS EVALUATION METRICS SCORECARD [0.0 - 1.0]")
    print(result)
    print("\n" + "="*40)
    print(f"\nDetailed CSV saved to {output_path}")

if __name__ == "__main__":
    run_evaluation()
