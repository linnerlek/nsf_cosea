import pandas as pd

# Define dictionary mapping original columns to readable names
column_dict = {
    "SE_A04001_001": "Total Population",
    "SE_A04001_002": "White Alone",
    "SE_A04001_003": "Black or African American Alone",
    "SE_A04001_004": "American Indian and Alaska Native Alone",
    "SE_A04001_005": "Asian Alone",
    "SE_A04001_006": "Native Hawaiian and Other Pacific Islander",
    "SE_A04001_007": "Some Other Race Alone",
    "SE_A04001_008": "Two or More Races",
    "SE_A04001_009": "Hispanic or Latino",
    "SE_A04001_010": "White Alone, Not Hispanic or Latino",
    "SE_A04001_011": "Median Age",
    "SE_A04001_012": "Male Population",
    "SE_A04001_013": "Female Population",
    "SE_A04001_014": "Population Under 18",
    "SE_A04001_015": "Population 65 and Over",
    "SE_A04001_016": "Foreign Born Population",
    "SE_A04001_017": "Non-English Speaking Households",
    "SE_A12001_001": "Total Households",
    "SE_A12001_002": "Married-Couple Family Households",
    "SE_A12001_003": "Single-Parent Family Households",
    "SE_A12001_004": "Nonfamily Households",
    "SE_A12001_005": "Households with Individuals < 18",
    "SE_A12001_006": "Households with Individuals 65+",
    "SE_A12001_007": "Average Household Size",
    "SE_A12001_008": "Average Family Size",
    "SE_A14006_001": "Median Household Income",
    "SE_A14007_001": "Per Capita Income"
}

# Convert to DataFrame
df = pd.DataFrame(list(column_dict.items()), columns=["original_column", "readable_name"])

# Save to CSV
df.to_csv("column_dictionary.csv", index=False)
print("Dictionary CSV file created: column_dictionary.csv")
