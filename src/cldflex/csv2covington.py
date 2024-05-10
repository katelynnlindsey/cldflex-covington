import pandas as pd

import re


def replace_reduplication(text):
    text = re.sub(r' ', '~', text, flags=re.IGNORECASE)
    text = re.sub(r'INF', 'INF~', text, flags=re.IGNORECASE)

    return text



def convert_ipa(text):
    # Perform replacements using regular expressions
    text = re.sub(r'tt', 'ʈʂ͡', text, flags=re.IGNORECASE)
    text = re.sub(r'dd', 'ɖʐ͡', text, flags=re.IGNORECASE)
    text = re.sub(r'll', 'ɽ', text, flags=re.IGNORECASE)
    text = re.sub(r'ny', 'ɲ', text, flags=re.IGNORECASE)
    text = re.sub(r'ng', 'ŋ', text, flags=re.IGNORECASE)
    text = re.sub(r'ɨ', 'ɪ', text, flags=re.IGNORECASE)
    text = re.sub(r'(ä|ä)', 'ə', text, flags=re.IGNORECASE)
    text = re.sub(r'ao', 'aw', text, flags=re.IGNORECASE)
    text = re.sub(r'ae', 'aj', text, flags=re.IGNORECASE)
    text = re.sub(r'oe', 'oj', text, flags=re.IGNORECASE)
    text = re.sub(r'y', 'j', text, flags=re.IGNORECASE)
    text = re.sub(r'g', 'ɡ', text, flags=re.IGNORECASE)

    # Convert the text to lowercase
    text = text.lower()

    # Remove punctuation characters (.,;:)
    text = re.sub(r'[\.,;:]', '', text)

    return text


def remove_exception(text):
    text = text.replace('=watt==a=watt=a', '=watt=a')
    text = text.replace('=att==a=att=a', '=att=a')

    return text


def convert_leipzig(gloss):
    # Replace underscores with \_
    gloss = gloss.replace('_', '\\_')

    # Replace GLS with {/Gls}
    gloss = gloss.replace('=ABL==NOM=ABL=NOM', '=ABL=NOM')
    gloss = gloss.replace('AGT', '{\\Agt}')
    gloss = gloss.replace('ALR', '{\\Alr}')
    gloss = gloss.replace('ANIM', '{\\Anim}')
    gloss = gloss.replace('APPL', '{\\Appl}')
    gloss = gloss.replace('ATR', '{\\Atr}')
    gloss = gloss.replace('AUX', '{\\Aux}')
    gloss = gloss.replace('CL.POSS', '{\\Clposs}')
    gloss = gloss.replace('COM', '{\\Com}')
    gloss = gloss.replace('COP', '{\\Cop}')
    gloss = gloss.replace('CTFL', '{\\Ctfl}')
    gloss = gloss.replace('DEM', '{\\Dem}')
    gloss = gloss.replace('DIM', '{\\Dim}')
    gloss = gloss.replace('DIS', '{\\Dis}')
    gloss = gloss.replace('DUR', '{\\Dur}')
    gloss = gloss.replace('EMPH', '{\\Emph}')
    gloss = gloss.replace('HAB', '{\\Hab}')
    gloss = gloss.replace('Q', '{\\Q}')
    gloss = gloss.replace('INTR', '{\\Intr}')
    gloss = gloss.replace('INT', '{\\Int}')
    gloss = gloss.replace('NDU', '{\\Ndu}')
    gloss = gloss.replace('NSG', '{\\Nsg}')
    gloss = gloss.replace('NPL', '{\\Npl}')
    gloss = gloss.replace('NPRS', '{\\Nprs}')
    gloss = gloss.replace('PERL', '{\\Perl}')
    gloss = gloss.replace('POT', '{\\Pot}')
    gloss = gloss.replace('POSS', '{\\Poss}')
    gloss = gloss.replace('PLUR', '{\\Plur}')
    gloss = gloss.replace('PRIV', '{\\Priv}')
    gloss = gloss.replace('PROX', '{\\Prox}')
    gloss = gloss.replace('REM', '{\\Rem}')
    gloss = gloss.replace('REC', '{\\Rec}')
    gloss = gloss.replace('REST', '{\\Rest}')
    gloss = gloss.replace('RT.EXT', '{\\Rtext}')
    gloss = gloss.replace('SIM', '{\\Sim}')
    gloss = gloss.replace('SMLT', '{\\Smlt}')
    gloss = gloss.replace('VEN', '{\\Ven}')
    gloss = gloss.replace('IV', '{\\Iv}')
    gloss = gloss.replace('III', '{\\Iii}')
    gloss = gloss.replace('II', '{\\Ii}')
    gloss = gloss.replace('I.', '{\\I}.')
    gloss = gloss.replace('`S', '{\\Sarg}')
    gloss = gloss.replace('`A', '{\\Aarg}')
    gloss = gloss.replace('`P', '{\\Parg}')
    gloss = gloss.replace('DU', '{\\Du}')
    gloss = gloss.replace('TR', '{\\Tr}')
    gloss = gloss.replace('CHAR', '{\\Char}')
    gloss = gloss.replace('PST', '{\\Pst}')
    gloss = gloss.replace('IRR', '{\\Irr}')
    gloss = gloss.replace('NPFV', '{\\Npfv}')
    gloss = gloss.replace('VOC', '{\\Voc}')
    gloss = gloss.replace('FUT', '{\\Fut}')
    gloss = gloss.replace('ALL', '{\\All}')
    gloss = gloss.replace('ACC', '{\\Acc}')
    gloss = gloss.replace('SG', '{\\Sg}')
    gloss = gloss.replace('1', '{\\First}')
    gloss = gloss.replace('2', '{\\Second}')
    gloss = gloss.replace('3', '{\\Third}')
    gloss = gloss.replace('LOC', '{\\Loc}')
    gloss = gloss.replace('|A', '|{\\Aarg}')
    gloss = gloss.replace('PL', '{\\Pl}')
    gloss = gloss.replace('NOM', '{\\Nom}')
    gloss = gloss.replace('INCL', '{\\Incl}')
    gloss = gloss.replace('INF', '{\\Inf}')
    gloss = gloss.replace('MED', '{\\Med}')
    gloss = gloss.replace('PRS', '{\\Prs}')
    gloss = gloss.replace('ABL', '{\\Abl}')

    return gloss


def convert_1toOne(number):

    # Replace GLS with {/Gls}
    number = number.replace('0', 'zero')
    number = number.replace('1', 'one')
    number = number.replace('2', 'two')
    number = number.replace('3', 'three')
    number = number.replace('4', 'four')
    number = number.replace('5', 'five')
    number = number.replace('6', 'six')
    number = number.replace('7', 'seven')
    number = number.replace('8', 'eight')
    number = number.replace('9', 'nine')
    number = number.replace('-', '')
    number = number.replace('.', 'point')

    return number


def convert_quotes(quotes):

    # Replace GLS with {/Gls}
    quotes = quotes.replace(' "', ' ``')

    return quotes


def csv_to_latex_commands(csv_file_path, output_file_path, output2_file_path):
    # Read the CSV file
    df = pd.read_csv(csv_file_path, header=0)

    # Open the output file for writing LaTeX commands
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        # Write introductory text (before processing CSV lines)
        intro_text = ""
        output_file.write(intro_text)

        # Iterate through each line in the CSV file
        for index, line in df.iterrows():
            # Extract data from the line
            # Adjust the indices according to your CSV structure
            example_id = str(line.iloc[6])[:9]  # Convert to string if necessary and take the first 9 characters

            # Add the contents of line[7] to example_id
            example_id += f"dash{str(line.iloc[7])}"

            # If line[8] is not blank, add its contents to example_id preceded by a period
            if pd.notnull(line.iloc[8]) and line.iloc[8] != "":
                example_id += f"dot{str(line.iloc[8])}"

            example_id = convert_1toOne(str(example_id))

            sentence = convert_quotes(str(line.iloc[24]))   # Sentence (e.g., 'Ttoen a ngasnges atta gänyan Llamda Kurupel bäne.')

            morph_analysis = convert_ipa(remove_exception(str(line.iloc[2])))  # Morpheme breakdown (e.g., 'ttoen=a	ngas~nges=att=a	gänya=n	llamda=Kurupel=bäne')

            gloss = convert_leipzig(str(line.iloc[3]))  # Gloss (e.g., 'story={\Nom} {\Inf}~do={\Abl}={\Nom}...')

            translation = convert_quotes(str(line.iloc[4]))  # Translation (e.g., 'This story is about what Old Man Kurupel did.')

            text_id = str(line.iloc[6])[:8].upper().replace('-', '\\_')

            line_id = str(line.iloc[7])
            if pd.notnull(line.iloc[8]) and line.iloc[8] != "":
                line_id += f".{str(line.iloc[8])[:1]}"

            citation = str(line.iloc[6])[9:]  # Get everything in line[6] after the 8th character
            citation = citation.capitalize()

            # Create the LaTeX command using the data from the line
            latex_command = f"""
\\newcommand{{\\{example_id}}}
{{
\\digloss[ex,fsi={{\\{'normalfont\\upshape'}}},fspreamble={{\\{'normalfont\\itshape'}}},
                preamble={{{sentence}}}, 
                postamble={{\\\\ \\hfill \\parencite[{text_id} \\#{line_id}]{{{citation}}}
                \\label{{{example_id}}}}}]
    {{{morph_analysis}}}
    {{{gloss}}}
    {{{translation}}}
}}

"""

            # Write the LaTeX command to the output file
            output_file.write(latex_command)
            output_file.write('\n')  # Add a newline for separation

            # Print progress
            print(f"Processed line {index + 1}...")

        # Write concluding text (after processing CSV lines)
        conclusion_text = ""
        output_file.write(conclusion_text)

    print(f"LaTeX commands saved to {output_file_path}")

    with open(output2_file_path, 'w') as output2_file:
        # Write introductory text (before processing CSV lines)
        intro_text = ("\\documentclass[Bk_Ende-grammar.tex]{subfiles}" "\n"
                      "\\graphicspath{{\\subfix{../images/}}}""\n"
                      "\\begin{document}""\n")
        output2_file.write(intro_text)

        for index, line in df.iterrows():
            example_id = str(line.iloc[6])[:9]
            example_id += f"dash{str(line.iloc[7])}"
            if pd.notnull(line.iloc[8]) and line.iloc[8] != "":
                example_id += f"dot{str(line.iloc[8])}"
            example_id = convert_1toOne(str(example_id))
            latex2_command = str(f"\\{str(example_id)}")
            output2_file.write(latex2_command)
            output2_file.write('\n')
            print(f"Processed line {index + 1}...")

        # Write concluding text (after processing CSV lines)
        conclusion_text = "\\end{document}"
        output2_file.write(conclusion_text)

    print(f"LaTeX commands saved to {output2_file_path}")

