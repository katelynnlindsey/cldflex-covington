from flex2csv import convert
from csv2covington import csv_to_latex_commands


def convert_flex2covington(input_flextext_path, output_csv_path, output_sty_path):
    convert(input_flextext_path,
            lexicon_file = None,
            conf = None,
            output_dir = output_csv_path,
            cldf = False,
            audio_folder = None)
    csv_to_latex_commands(output_csv_path, output_sty_path)


input_flextext_path = 'C:\\Users\\profk\\Desktop\\OpenTextCollection.flextext'
output_csv_path = 'examples.csv'
output_sty_path = 'examples.sty'

convert_flex2covington(input_flextext_path, output_csv_path, output_sty_path)