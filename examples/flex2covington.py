import os
from src.cldflex.flex2csv import convert
from src.cldflex.csv2covington import csv_to_latex_commands
from pathlib import Path

def convert_flex2covington():
    # Specify the input .flextext file and output directory for the first script
    flex_file = "data/ende.flextext"
    output_directory = Path("C:\\Users\\profk\\PycharmProjects\\cldflex-covington\\examples\\data\\output")

    # Convert flextext to csv and save to the output directory
    convert(flextext_file=flex_file, output_dir=output_directory)

    # Determine the name of the CSV file based on the .flextext file name
    # Extract the base name of the flextext file (without the file extension)
    base_name = os.path.splitext(os.path.basename(flex_file))[0]

    # Construct the path to the generated .csv file in the output directory
    csv_file = output_directory / "examples.csv"

    # Specify the output .sty and .tex file
    sty_file = output_directory / f"{base_name}.sty"
    tex_file = output_directory / f"{base_name}.tex"

    # Convert csv to sty
    csv_to_latex_commands(csv_file, sty_file, tex_file)

    # Let the user know the process is complete
    print(f"Conversion complete! {sty_file} and {tex_file} files created.")


if __name__ == "__main__":
    convert_flex2covington()

