import subprocess
import os
from cldflex.flex2csv import convert
from cldflex.csv2covington import csv_to_latex_commands


def convert_flex2covington():
    # Specify the input .flextext file and output directory for the first script
    flex_file = "\data\ende.flextext"
    output_directory = "\output"

    # Convert flextext to csv and save to the output directory
    convert(flextext_file=flex_file, output_dir=output_directory)

    # Determine the name of the CSV file based on the .flextext file name
    # Extract the base name of the flextext file (without the file extension)
    base_name = os.path.splitext(os.path.basename(flextext_file))[0]

    # Construct the path to the generated .csv file in the output directory
    csv_file = os.path.join(output_directory, f"{base_name}.csv")

    # Specify the output .sty and .tex file
    sty_file = f"\output\\{base_name}.sty"
    tex_file = f"\output\\{base_name}.tex"

    # Convert csv to sty
    csv_to_latex_commands(csv_file, sty_file, tex_file)

    # Let the user know the process is complete
    print(f"Conversion complete! {sty_file} and {tex_file} files created.")

if __name__ == "__main__":
    main()