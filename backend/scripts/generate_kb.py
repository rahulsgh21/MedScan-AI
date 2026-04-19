import os
from pathlib import Path
import shutil

KNOWLEDGE_DIR = Path("c:/Users/rs725/Desktop/New_projects/MedScan-AI/backend/app/knowledge")
BIOMARKER_DIR = KNOWLEDGE_DIR / "biomarker_info"
LIFESTYLE_DIR = KNOWLEDGE_DIR / "lifestyle_tips"

BIOMARKER_DIR.mkdir(parents=True, exist_ok=True)
LIFESTYLE_DIR.mkdir(parents=True, exist_ok=True)

BIOMARKERS = {
    "amylase_lipase.md": """# Amylase and Lipase (Pancreatic Enzymes)

## What They Measure
Amylase and lipase are enzymes produced primarily by the pancreas to help digest carbohydrates and fats, respectively. 

## Why is it Important?
Elevated levels strongly indicate pancreatic inflammation (pancreatitis) or other pancreatic diseases. Lipase is generally more specific to the pancreas than amylase.

## Normal Ranges
- **Amylase:** 30 - 110 U/L
- **Lipase:** 0 - 160 U/L

## What HIGH Levels Mean
- **Acute Pancreatitis:** The most common cause. Levels can rise to 3-10 times the upper normal limit.
- **Other Causes:** Gallstones blocking the pancreatic duct, heavy alcohol consumption, severe gastroenteritis, or peptic ulcers.

## What LOW Levels Mean
Usually not clinically significant, but extremely low levels might indicate permanent damage to insulin-producing cells (chronic pancreatitis or cystic fibrosis).

## Lifestyle & Diet Recommendations
- **Strictly Avoid Alcohol:** Alcohol is a leading trigger for pancreatic inflammation.
- **Low-Fat Diet:** Switch to easily digestible foods. Avoid deeply fried foods, rich curries (gravies with heavy cream/butter), and fast food.
- **Hydration:** Drink plenty of water (coconut water and clear broths are excellent).
- **Herbal Adjustments:** Mild ginger tea can help soothe digestion, but avoid very spicy masalas.

## Questions to Ask Your Doctor
- "Do I need an ultrasound or a CT scan of my abdomen to check for gallstones?"
- "Should I temporarily switch to a liquid or semi-solid diet?"
""",

    "cardiac_markers.md": """# Cardiac Markers (Troponin, CPK, CK-MB)

## What They Measure
These tests measure enzymes and proteins released into the bloodstream when the heart muscle is damaged. 
- **Troponin (I or T):** The gold standard protein marker for heart damage.
- **CPK / CK-MB:** An enzyme found in the heart, brain, and skeletal muscle.

## Why is it Important?
These are critical, emergency markers used to diagnose a heart attack (Myocardial Infarction). Troponin can remain elevated for days after a heart event.

## Normal Ranges
- **Troponin I:** < 0.04 ng/mL (highly dependent on the lab and assay type)
- **CPK (Total):** 22 - 198 U/L
- **CK-MB:** < 5% of total CPK or < 5 ng/mL

## What HIGH Levels Mean
- **Critical Alert:** Elevated Troponin or CK-MB usually means acute heart muscle damage (Heart Attack/Myocardial Infarction). **This requires immediate medical hospitalization.**
- **Other Causes:** Severe kidney disease, pulmonary embolism, severe strenuous exercise (can raise total CPK), or chronic heart failure.

## Lifestyle & Diet Recommendations
*Note: High cardiac markers demand emergency medical intervention. Lifestyle tips apply for post-event recovery.*
- **Heart-Healthy Diet:** Adopt a Mediterranean-style diet. In the Indian context, this means cooking with healthy oils (olive, mustard, or groundnut instead of excessive saturated ghee/butter), eating more leafy greens, and increasing omega-3 (flaxseeds, walnuts, fatty fish).
- **Reduce Sodium (Salt):** Limit salt intake to manage blood pressure (avoid papad, pickles, namkeen).
- **Gradual Cardiac Rehab:** Post-event, engage only in medically supervised light activities like walking. Avoid heavy lifting.
- **Quit Smoking Immediately:** Crucial for heart health.

## Questions to Ask Your Doctor
- "If my Troponin is high, what are our immediate next steps? Do I need an angiography?"
- "Are there any medications (like statins or thinners) I should start immediately?"
""",

    "crp_esr.md": """# Inflammatory Markers (CRP and ESR)

## What They Measure
- **CRP (C-Reactive Protein):** A protein produced by the liver in response to acute inflammation.
- **ESR (Erythrocyte Sedimentation Rate):** A measure of how quickly red blood cells settle at the bottom of a test tube; faster settling indicates systemic inflammation.

## Why is it Important?
They are non-specific markers. They don't tell you *where* the inflammation is, but they tell you that inflammation, infection, or tissue damage is happening *somewhere* in the body.

## Normal Ranges
- **CRP:** < 10 mg/L (hs-CRP used for heart risk is typically < 1.0 mg/L for low risk)
- **ESR:** Men: 0 - 15 mm/hr, Women: 0 - 20 mm/hr

## What HIGH Levels Mean
- **Infection:** Bacterial or viral infections (e.g., Dengue, Typhoid, COVID-19, severe throat/lung infections).
- **Autoimmune Disorders:** Rheumatoid arthritis, lupus, inflammatory bowel disease.
- **Tissue Damage:** From trauma, burns, or a recent heart attack.

## Lifestyle & Diet Recommendations
To reduce systemic inflammation:
- **Anti-Inflammatory Spices:** Include Turmeric (Haldi) with black pepper, and ginger in your daily diet. Curcumin in turmeric is a potent anti-inflammatory.
- **Omega-3 Fatty Acids:** Consume chia seeds, flaxseeds, and walnuts.
- **Avoid Ultra-Processed Foods:** Cut down on refined flour (maida), refined sugar, and deep-fried packaged snacks, which fuel inflammation.
- **Weight Management:** Excess fat tissue releases inflammatory chemicals. Gradual weight loss helps lower baseline CRP.

## Questions to Ask Your Doctor
- "Since these tests are non-specific, what other tests should we run to find the source of the inflammation?"
- "Could my joint pain/fever be related to these high marker levels?"
""",

    "vitamin_b12_d.md": """# Vitamin B12 and Vitamin D

## What They Measure
- **Vitamin B12:** Essential for nerve tissue health, brain function, and the production of red blood cells.
- **Vitamin D (25-OH):** Crucial for calcium absorption, bone health, and immune function.

## Why is it Important?
Deficiencies are extremely common, especially in India, despite abundant sunlight. Prolonged deficiency leads to permanent nerve damage, severe fatigue, brittle bones, and weakened immunity.

## Normal Ranges
- **Vitamin B12:** 200 - 900 pg/mL
- **Vitamin D:** 30 - 100 ng/mL

## What LOW Levels Mean (Deficiency)
- **Low B12:** Can cause pernicious anemia, tingling/numbness in hands/feet, memory loss, and extreme fatigue. *Very common in strict vegetarians/vegans.*
- **Low Vitamin D:** Leads to bone and back pain, muscle weakness, hair loss, and increased susceptibility to infections. Severe deficiency causes rickets in children and osteomalacia in adults.

## Lifestyle & Diet Recommendations
### For B12 Deficiency:
- **Animal Sources:** Incorporate eggs, fish, poultry, and meat if you are non-vegetarian.
- **Vegetarian Sources:** Dairy products (milk, paneer, curd) and fortified cereals/plant milks.
- **Supplements:** Strictly vegetarian/vegan diets often require B12 supplements (cyanocobalamin or methylcobalamin).

### For Vitamin D Deficiency:
- **Sunlight:** Spend 15-20 minutes in the direct sun (preferably mid-morning) without sunscreen a few times a week, exposing arms and legs.
- **Diet:** Consume egg yolks, mushrooms exposed to sunlight, and fortified milk.
- **Supplements:** Dietary sources are usually insufficient for severe deficiency; high-dose weekly supplements (like 60,000 IU cholecalciferol) are often prescribed.

## Questions to Ask Your Doctor
- "Are oral supplements enough, or do I need Vitamin B12/Vitamin D injections?"
- "Should I get a bone density scan (DEXA) due to my prolonged Vitamin D deficiency?"
""",

    "uric_acid.md": """# Uric Acid

## What It Measures
Uric acid is a waste product created when the body breaks down chemicals called purines, which are found in certain foods and cells. It normally dissolves in blood, passes through the kidneys, and exits via urine.

## Why is it Important?
If your body produces too much or removes too little, uric acid builds up and forms sharp, needle-like crystals in the joints (typically the big toe), causing a painful condition called Gout. It can also cause kidney stones.

## Normal Range
- **Adult Male:** 3.4 - 7.0 mg/dL
- **Adult Female:** 2.4 - 6.0 mg/dL

## What HIGH Levels Mean (Hyperuricemia)
- **Gout:** The primary risk. Causes extreme joint pain, redness, and swelling.
- **Kidney Stones:** Urate crystals can form stones in the renal system.
- **Metabolic Syndrome:** Often associated with obesity, high blood pressure, and insulin resistance.

## Lifestyle & Diet Recommendations
- **Avoid High-Purine Foods:** Red meat, organ meats, and certain seafood (sardines, shellfish).
- **Vegetarian Triggers:** While plant purines are generally safer, excessive intake of lentils (daal), spinach (palak), and cauliflower during an acute attack may aggravate symptoms for some individuals. 
- **Avoid Fructose and Alcohol:** Beer and sugary drinks (especially high-fructose corn syrup) drastically increase uric acid production.
- **Hydration:** Drink plenty of water (at least 3 liters/day) to help the kidneys flush out uric acid.
- **Helpful Foods:** Cherries, lemon water, and low-fat dairy can actively help lower uric acid levels.

## Questions to Ask Your Doctor
- "Do I need medications to lower uric acid, or can I manage this with diet alone?"
- "Should I take pain relievers specifically for gout attacks (like colchicine)?"
""",

    "hormones_testosterone_cortisol.md": """# Hormones (Testosterone & Cortisol)

## What They Measure
- **Testosterone:** The primary male sex hormone, also present in smaller amounts in females. Crucial for muscle mass, bone density, libido, and energy.
- **Cortisol:** The body's main stress hormone, produced by the adrenal glands. It regulates metabolism, reduces inflammation, and controls the sleep-wake cycle.

## Normal Ranges (Vary widely by age and lab)
- **Testosterone (Total, Adult Male):** 300 - 1000 ng/dL
- **Testosterone (Total, Adult Female):** 15 - 70 ng/dL
- **Cortisol (Morning 8 AM):** 5 - 25 mcg/dL

## What ABNORMAL Levels Mean
- **Low Testosterone (Men):** Can cause fatigue, depression, low libido, erectile dysfunction, and loss of muscle mass. Often caused by aging, obesity, or hypogonadism.
- **High Testosterone (Women):** Often associated with Polycystic Ovary Syndrome (PCOS), leading to irregular periods, acne, and excess facial hair.
- **High Cortisol:** Often due to chronic stress. In severe cases, Cushing's syndrome (causing weight gain, high BP, round face).
- **Low Cortisol:** Adrenal insufficiency (Addison's disease), severe fatigue, low blood pressure.

## Lifestyle & Diet Recommendations
### To Support Healthy Testosterone:
- **Strength Training:** Resistance exercises (weightlifting) are proven to safely boost testosterone.
- **Adequate Fats:** Ensure sufficient intake of healthy fats (ghee, mixed nuts, seeds) as cholesterol is the building block of hormones.
- **Zinc & Vitamin D:** Consume pumpkin seeds and eggs.

### To Manage Cortisol:
- **Stress Reduction:** Practice Yoga, Pranayama (deep breathing), and meditation. Ashwagandha (an adaptogenic herb) is clinically shown to help reduce cortisol.
- **Sleep:** 7-8 hours of uninterrupted sleep is mandatory. Lack of sleep spikes cortisol.
- **Limit Caffeine:** Reduce coffee/tea intake, especially in the late afternoon/evening.

## Questions to Ask Your Doctor
- "Should we check my Free Testosterone or SHBG levels for better accuracy?"
- "Is my cortisol high due to stress, or should we do a suppression test to check adrenal function?"
""",

    "infectious_serology.md": """# Infectious Serology & Antibodies (Dengue, Typhoid, Hepatitis)

## What They Measure
These tests detect to the presence of antigens (the virus/bacteria itself) or antibodies (your immune response) to specific infections.
- **IgM Antibodies:** Indicate an *active or recent* infection.
- **IgG Antibodies:** Indicate a *past* infection or immunity (from a prior exposure or vaccine).

## Common Tests
- **Dengue NS1 Antigen:** Positive in the first 1-5 days of Dengue fever.
- **Dengue IgM / Leptospira IgM / Scrub Typhus IgM:** Positive during the active phase of the fever.
- **Typhoid (Widal / Typhidot):** Tests for Salmonella typhi antibodies.
- **Hepatitis B (HBsAg):** Surface antigen test. Positive means active infection.
- **HCV Antibody:** Tests for exposure to Hepatitis C.

## What ABNORMAL (Positive/Reactive) Means
- A **Positive or Reactive** IgM or Antigen test means you currently have the illness. This explains fevers, body aches, fatigue, and organ stress.
- A **Positive IgG** (with a negative IgM/Antigen) usually just means you are immune or had it in the past. It is NOT a cause for current concern.

## Lifestyle & Diet Recommendations (During Active Infection)
- **Extreme Hydration:** Fevers (especially Dengue) cause rapid dehydration. Drink ORS (Oral Rehydration Solution), tender coconut water, and fresh fruit juices (like Mosambi/sweet lime without sugar) continuously.
- **Platelet Support (Dengue):** Papaya leaf extract/juice and kiwi are commonly recommended in Indian households to support platelet recovery, though clinical evidence varies — maintaining hydration is medically the most critical step.
- **Bland Diet (Typhoid/Hepatitis):** The digestive system or liver is inflamed. Eat extremely bland, soft foods: Khichdi, curd-rice (dahi chawal), boiled potatoes.
- **Complete Rest:** Avoid any physical exertion.

## Questions to Ask Your Doctor
- "(If Dengue) How often should we monitor my Complete Blood Count (CBC) to watch platelet levels?"
- "Are antibiotics needed for this, or is it viral and requiring only supportive care?"
""",

    "tumor_markers.md": """# Tumor Markers (PSA, CA-125, CEA)

## What They Measure
Tumor markers are substances (often proteins) produced by cancer tissue or by the body in response to cancer growth. 
- **PSA (Prostate-Specific Antigen):** Screened in men for prostate health.
- **CA-125:** Monitored primarily for ovarian cancer.
- **CEA (Carcinoembryonic Antigen):** Monitored for colorectal and some other digestive cancers.

## Why is it Important?
They are used to screen for cancer, evaluate how well cancer treatment is working, or check if cancer has returned. **Note: A high tumor marker does NOT automatically mean cancer.** Many non-cancerous conditions can raise these levels.

## Normal Ranges
- **PSA:** < 4.0 ng/mL (limits adjust slightly higher for older men)
- **CA-125:** < 35 U/mL
- **CEA:** < 3.0 ng/mL (non-smokers); < 5.0 ng/mL (smokers)

## What HIGH Levels Mean
- **PSA:** Could mean Prostate Cancer, but is very frequently raised by BPH (Benign Prostatic Hyperplasia - enlarged prostate) or prostatitis (infection).
- **CA-125:** Ovarian cancer, but also endometriosis, fibroids, menstruation, or pelvic inflammatory disease (PID).
- **CEA:** Colorectal cancer, but also elevated by smoking, gastritis, or inflammatory bowel disease.

## Lifestyle & Diet Recommendations
*Diet does not cure or diagnose cancer, but general health support is vital.*
- **Prostate Health (PSA):** Consume foods rich in Lycopene (cooked tomatoes, watermelon) and reduce high-fat dairy. Maintain regular physical activity.
- **General Antioxidants:** Eat a colorful diet rich in antioxidants (berries, greens, beetroot) to reduce cellular oxidative stress.
- **Avoid Known Carcinogens:** Stop all tobacco use (smoking or chewing). 

## Questions to Ask Your Doctor
- "Given that these markers can rise from non-cancerous issues, do I need a biopsy, MRI, or ultrasound to confirm?"
- "Should we repeat this test in a few weeks to see if it's trending upward or was just a temporary spike?"
"""
}

# General Lifestyle Tips
LIFESTYLE = {
    "stress_management.md": """# Stress Management & Cortisol Control

## Why It Matters
Chronic stress keeps your body in a persistent "fight-or-flight" mode. This constantly elevates the hormone Cortisol, which leads to high blood pressure, increased belly fat, disrupted sleep, weakened immunity, and insulin resistance. It can throw almost every lab test out of optimal bounds.

## Actionable Tips

### 1. Breathwork (Pranayama)
- **What to do:** Practice Anulom Vilom (alternate nostril breathing) or 4-7-8 breathing (inhale for 4s, hold for 7s, exhale for 8s) for just 5-10 minutes daily.
- **Why it works:** Deep, slow breathing physically signals your vagus nerve to turn off the stress response and lower heart rate.

### 2. Physical Release
- **What to do:** Engage in moderate exercise like brisk walking, swimming, or yoga. 
- **Caution:** Don't do extreme High-Intensity Interval Training (HIIT) if you are already severely stressed, as aggressive workouts can temporarily spike cortisol further.

### 3. Dietary Adjustments
- **Adaptogens:** Consider adding Ashwagandha or Tulsi (Holy Basil) tea to your routine. These herbs have been shown in studies to blunt the stress response.
- **Magnesium:** Often depleted by stress. Eat magnesium-rich foods like pumpkin seeds, almonds, and spinach.

### 4. Digital Detox
- **What to do:** Stop consuming doom-scrolling news or fast-paced social media at least 1 hour before bed.

## Questions to Ask Your Doctor
- "Could stress be directly causing my elevated blood pressure / blood sugar readings?"
- "Is my fatigue related to adrenal fatigue or stress burnout?"
""",

    "sleep_hygiene.md": """# Sleep Hygiene & Restoration

## Why It Matters
Sleep is when the body physically repairs tissue, clears out brain toxins, and balances hormones (like insulin and growth hormone). Poor sleep guarantees poor lab results over time, particularly for blood sugar control, inflammatory markers, and cardiovascular health.

## Actionable Tips

### 1. Establish a Biological Rhythm
- **Consistency:** Go to bed and wake up at the exact same time every day, even on weekends. Doing this establishes your circadian rhythm and optimizes melatonin production.

### 2. Light Management
- **Morning:** Get natural sunlight in your eyes within 30 minutes of waking up. This signals your brain to halt melatonin and produce daytime hormones.
- **Evening:** Avoid blue light (phones, laptops, bright LEDs) for 1-2 hours before bed. Use blue-light-blocking glasses or "night mode" on devices.

### 3. Optimize the Environment
- **Temperature:** Keep your bedroom cool (around 18–20°C or 65–68°F). The body needs to drop its core temperature to initiate deep sleep.
- **Darkness:** Make the room pitch black. Use blackout curtains or an eye mask.

### 4. Evening Routine
- **Avoid Stimulants:** No caffeine (coffee, strong tea, cola) after 2 PM. Caffeine has a quarter-life of 10-12 hours in some individuals.
- **Wind Down:** Take a warm shower before bed; the rapid cooling of your body afterward helps trigger sleepiness.
- **Heavy Meals:** Avoid eating heavy, spicy, or high-sugar meals within 3 hours of sleeping. It disrupts the deep sleep cycles.
"""
}

# Write text to files
print("Generating Biomarker Markdown files...")
for filename, content in BIOMARKERS.items():
    with open(BIOMARKER_DIR / filename, "w", encoding="utf-8") as f:
        f.write(content)
        
print("Generating Lifestyle Markdown files...")
for filename, content in LIFESTYLE.items():
    with open(LIFESTYLE_DIR / filename, "w", encoding="utf-8") as f:
        f.write(content)

print("Markdown generations complete. 11 new knowledge files created.")

# Now trigger the DB ingestion
import sys
# Add parent dir to path so we can import the app
sys.path.append(str(Path(__file__).parent.parent))

print("Connecting to Vector Store to re-ingest data...")
from app.services.vector_store import get_vector_store

# Get instance
kb = get_vector_store()
# Force clean collection to prevent duplicates
client = kb.chroma_client
try:
    client.delete_collection("medical_knowledge")
    print("Old collection deleted.")
except Exception as e:
    print("No old collection found.")

# Re-create and ingest
kb.collection = client.create_collection(
    name="medical_knowledge",
    embedding_function=kb.embedding_fn
)
kb.ingest_data()

print("✅ SUCCESS: Knowledge Base Expanded and Vector Store Updated!")
