import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from sentence_transformers import SentenceTransformer, util

def evaluate_similarity():
    print("Loading both Semantic Models (This may take a moment)...\n")
    
    # 1. Load Old Generalist Model
    print("Loading Old Model: all-MiniLM-L6-v2...")
    model_old = SentenceTransformer("all-MiniLM-L6-v2")
    
    # 2. Load New Specialized Medical Model
    print("Loading New Model: pritamdeka/S-PubMedBert-MS-MARCO...")
    model_new = SentenceTransformer("pritamdeka/S-PubMedBert-MS-MARCO")
    
    # 3. Medical Phrase Comparisons
    # The first phrase uses strict medical terminology, the second is plain English
    comparisons = [
        ("Hyperlipidemia", "High cholesterol"),
        ("Thrombocytopenia", "Low platelets in the blood"),
        ("Myocardial Infarction", "Heart attack"),
        ("Renal Failure", "The kidneys stopped working properly")
    ]
    
    print("\n" + "="*60)
    print("SEMANTIC SIMILARITY COMPARISON: MiniLM vs PubMedBERT")
    print("="*60 + "\n")
    
    for phrase1, phrase2 in comparisons:
        # Encode phrase pairs
        old_emb1 = model_old.encode(phrase1, convert_to_tensor=True)
        old_emb2 = model_old.encode(phrase2, convert_to_tensor=True)
        
        new_emb1 = model_new.encode(phrase1, convert_to_tensor=True)
        new_emb2 = model_new.encode(phrase2, convert_to_tensor=True)
        
        # Calculate Cosine Similarity (0 to 1 score)
        score_old = util.cos_sim(old_emb1, old_emb2).item()
        score_new = util.cos_sim(new_emb1, new_emb2).item()
        
        print(f"Phrase 1: '{phrase1}'")
        print(f"Phrase 2: '{phrase2}'")
        print(f"  Old score (MiniLM):      {score_old:.2f}")
        print(f"  New score (PubMedBERT):  {score_new:.2f}")
        
        # Calculate percentage difference
        diff = ((score_new - score_old) / score_old) * 100
        print(f"  Difference:              {diff:+.1f}% shift in understanding\n")

if __name__ == "__main__":
    evaluate_similarity()
