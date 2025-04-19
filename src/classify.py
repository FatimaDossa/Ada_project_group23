import pandas as pd

df = pd.read_csv("../data/data.csv", dtype=str)

# Define ICD codes for each category
urgent_codes = [
    "J18.9", "P07.30", "S06.0X0A", "A41.9", "I21.9", 
    "U07.1", "T14.91", "R07.9", "L03.90"
]

chronic_codes = [
    "E11.9", "J45.9", "B20", "M54.5", "Q21.1", "G43.9", "G40.9", "Z51.11"
]

non_urgent_codes = [
    "N39.0", "K35.80", "I10", "K21.9", "G30.0", "F80.9"
]
# Label based on the ICD codes
def label_code(x):
    if x in urgent_codes:
        return 1  # Urgent
    elif x in chronic_codes:
        return 2  # Chronic/Stable
    elif x in non_urgent_codes:
        return 0  # Non-urgent
    else:
        return -1  # Unknown code (optional)

# Apply the labeling function
df['label'] = df['icd_code'].apply(label_code)
# save the updated dataframe back to the same file (or a new one)
df.to_csv("../data/data.csv", index=False)
# print(df['label'].value_counts())