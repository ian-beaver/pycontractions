import pandas as pd

# Comment out the clipboard readline if you are importing it manually
# Reading dataframe off of clipboard and formatting it
df = pd.read_clipboard() # Reading dataframe off clipboard
df.columns = ["Contraction", "Meaning"] # Renaming the columns
first_row = pd.DataFrame([["you've", "you have"]], columns=["Contraction", "Meaning"]) # Getting the data off of the column
df = df.append(first_row) # Attaching the first row to the dataframe

# Initializing contractions
contractions = {}

# Iterating through every row of the dataframe
for row_ix in range(len(df)):

    # Grabbing the row
    row = df.iloc[row_ix]

    # Grabbing the contraction from the respective row
    contraction = row["Contraction"]

    # Grabbing the meaning from the respective row
    meaning = row["Meaning"]

    # Grabbing multiple meanings from meaning, if any
    # Example: "do not / does not" -> ["do not", "does not"]
    if "/" in meaning:
        meanings = meaning.split(" / ")
    else:
        meanings = repr(meaning)

    # Formatting contraction
    if "\'" in contraction:
        contraction = "\'?".join(contraction.split("\'"))

    # Initializing regex statement
    regex_statement = "re.compile(r\"{}\", re.I | re.U)".format(contraction)

    contractions[regex_statement] = meanings


print(contractions)
