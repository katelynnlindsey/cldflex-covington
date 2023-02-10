import logging
import re
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import yaml
from bs4 import BeautifulSoup
from slugify import slugify
from cldflex.cldf import create_dictionary_dataset
from cldflex.cldf import create_rich_dataset
from cldflex.cldf import create_wordlist_dataset
from cldflex.helpers import add_to_list_in_dict
from cldflex.helpers import deduplicate
from cldflex.helpers import delistify
from cldflex.helpers import listify


log = logging.getLogger(__name__)


# method for getting dictionary examples from entries
def extract_examples(sense, dictionary_examples, sense_id):
    for ex_count, example in enumerate(sense.find_all("example")):
        example_dict = {"ID": f"{sense_id}-{ex_count}", "Sense_ID": sense_id}
        for child in example.find_all(recursive=False):
            if child.name == "form":
                example_dict["Primary_Text"] = child.text
            elif child.name == "translation":
                child_form = child.find("form")
                if child_form:
                    example_dict["Translated_Text"] = child_form.find("text").text
            else:
                child_form = child.find("form")
                if child_form:
                    example_dict[
                        f"{child.name}-{slugify(child['type'])}-{child_form['lang']}"
                    ] = child_form.text
                else:
                    log.warning(f"Sense {sense_id} has empty examples")
        for attr in example.attrs:
            example_dict[attr] = example[attr]
        dictionary_examples.append(example_dict)


def figure_out_gloss_language(entry):
    gloss_lg = None
    if entry.find("gloss"):
        gloss_lg = entry.find("gloss")["lang"]
    elif entry.find("definition"):
        gloss_lg = entry.find("definition").find("form")["lang"]
    if gloss_lg:
        log.info(f"Using [{gloss_lg}] as the main meta language ('Meaning' column)")
    return gloss_lg


def parse_entries(entries):
    parsed = []  # parsed entries
    senses = []  # gathered senses
    dictionary_examples = []  # gathered examples
    for entry in entries:
        rec = {
            "Gramm": [],
            "Senses": [],
        }  # the parsed entry, with different fields (i.e., CSV columns)
        rec["ID"] = entry["guid"]
        for trait in entry.find_all(
            "trait", recursive=False
        ):  # various traits, like morph-type
            rec[trait["name"]] = trait["value"]
        for lexical_unit in entry.find_all("lexical-unit", recursive=False):
            for form in lexical_unit.find_all("form"):
                rec["form_" + form["lang"]] = form.text
        for field in entry.find_all("field", recursive=False):
            for pseudoform in field.find_all("form"):
                rec[slugify(field["type"]) + "_" + pseudoform["lang"]] = pseudoform.text
        for relation in entry.find_all("relation", recursive=False):
            if "_" not in relation["ref"]:  # ignore relations without a reference
                continue
            for trait in relation.find_all("trait"):
                add_to_list_in_dict(
                    rec,
                    f"relation{relation['type']}_{trait['name']}_{slugify(trait['value'])}",
                    relation["ref"].split("_")[1],
                )
        for sense in entry.find_all("sense", recursive=False):
            sense_id = sense["id"]  # todo: human-readable option
            sense_dict = {"ID": sense_id, "Entry_ID": rec["ID"]}
            rec["Senses"].append(sense["id"])
            for gramm in sense.find_all("grammatical-info"):
                rec["Gramm"].append(gramm["value"])
            for definition in sense.find_all("definition"):
                for pseudoform in definition.find_all("form"):
                    for x in [rec, sense_dict]:
                        add_to_list_in_dict(
                            x, "definition_" + pseudoform["lang"], pseudoform.text
                        )
            for gloss in sense.find_all("gloss"):
                key = "gloss_" + gloss["lang"]
                for x in [rec, sense_dict]:
                    add_to_list_in_dict(x, key, gloss.text)
            for note in sense.find_all("note"):
                note_type = ("note_" + note.get("type", "")).strip("_")
                for pseudoform in note.find_all("form"):
                    add_to_list_in_dict(
                        rec, note_type + "_" + pseudoform["lang"], pseudoform.text
                    )
            for reversal in sense.find_all("reversal"):
                for form in reversal.find_all("form"):
                    add_to_list_in_dict(rec, "reversal_" + form["lang"], form.text)
            senses.append(sense_dict)
            extract_examples(sense, dictionary_examples, sense_id)

        for i, allomorph in enumerate(entry.find_all("variant", recursive=False)):
            form = allomorph.find("form")
            for trait in allomorph.find_all("trait", recursive=False):
                add_to_list_in_dict(rec, "variant_" + trait["name"], trait["value"])
            add_to_list_in_dict(rec, "variant_" + form["lang"], form.text)
        rec["Gramm"] = deduplicate(rec["Gramm"])
        parsed.append(rec)
    return parsed, senses, dictionary_examples


def convert(
    lift_file, output_dir=".", config_file=None, cldf=False, conf=None
):  # pylint: disable=too-many-locals
    if not lift_file.suffix == ".lift":
        log.error("Please provide a .lift file.")
        sys.exit()
    if not conf and not config_file:
        log.info("Running without configuration file or dict.")
        conf = {}
    elif not conf:
        with open(config_file, encoding="utf-8") as f:
            conf = yaml.safe_load(f)
    sep = conf.get(
        "csv_cell_separator", "; "
    )  # separator used in cells with multiple values

    log.info(f"Parsing {lift_file.resolve()}")
    with open(lift_file, "r", encoding="utf-8") as f:
        lexicon = BeautifulSoup(f.read(), features="xml")

    obj_lg = conf.get("obj_lg", None)  # main object language
    gloss_lg = conf.get("gloss_lg", None)  # main gloss language

    for entry in lexicon.find_all(
        "entry"
    ):  # if not defined, they are deducted from the data
        if not gloss_lg:
            gloss_lg = figure_out_gloss_language(entry)
        if not obj_lg:
            obj_lg = entry.find("form")["lang"]

    obj_key = f"form_{obj_lg}"  # <form lang="X"><text>Y</text></form> becomes form_X: Y
    definition_key = f"definition_{gloss_lg}"  # <definition><form lang="X"><text>Y</text></form></definition> becomes defition_X: Y
    gloss_key = (
        f"gloss_{gloss_lg}"  # <gloss lang="X"><text>Y</text></gloss> becomes X_gloss: Y
    )
    var_key = "variant_" + obj_lg

    var_dict = {}
    entries, senses, dictionary_examples = parse_entries(lexicon.find_all("entry"))
    entries = pd.DataFrame.from_dict(entries)
    senses = pd.DataFrame.from_dict(senses)

    for key in [definition_key, gloss_key]:
        if key not in senses.columns:
            senses[key] = np.nan
    # fill sense descriptions with glosses
    senses["Description"] = senses.apply(
        lambda x: x[definition_key]
        if not pd.isnull(x[definition_key])
        else x[gloss_key],
        axis=1,
    )
    # fill sense names with glosses and definitions

    senses["Name"] = senses.apply(
        lambda x: " / ".join(x[gloss_key])
        if not pd.isnull(x[gloss_key]).all()
        else x[definition_key],
        axis=1,
    )

    # method for printing entries in log
    def entry_repr(entry_id):
        entry = entries[entries["ID"] == entry_id].iloc[0]
        meanings = entry.get(gloss_key, entry.get(definition_key, ""))
        if not isinstance(meanings, list):
            ggg = "unknown meaning"
        elif len(meanings) == 0:
            ggg = "unknown meaning"
        else:
            ggg = " / ".join(meanings)
        if isinstance(entry.get("Form", None), list):
            form_str = " / ".join(entry["Form"])
        else:
            form_str = entry.get("Form", "MISSING FORM")
        return f"""{form_str} '{ggg}' ({','.join(entry["Gramm"])}, {entry["Type"]})"""

    entries.rename(
        columns={
            obj_key: "Form",
            var_key: "Variants",
            "Senses": "Parameter_ID",
            gloss_key: "Gloss",
            "morph-type": "Type",
        },
        inplace=True,
    )
    gloss_key = "Gloss"
    entries["Variants"] = entries["Variants"].apply(
        lambda d: d if isinstance(d, list) else []
    )
    entries["Language_ID"] = obj_lg

    # 1. find all variants
    # 2. compile dictionary mapping entry IDs to variants
    for col in entries.columns:
        if "variant-type" not in col:
            continue
        variants = entries[~(pd.isnull(entries[col]))]
        log.info(f"Parsing variants of type '{col} ({len(variants)} found)")
        for entry in variants.to_dict("records"):
            if len(entry[col]) > 1:
                msg = f"""The entry {entry_repr(entry["ID"])} is stored as a variant ({col}) of multiple main entries:"""
                for entry_id in entry[col]:
                    msg += "\n* " + entry_repr(entry_id)
                log.warning(msg)
            for entry_id in entry[col]:
                add_to_list_in_dict(var_dict, entry_id, entry)

    # listify gloss and variant columns
    for key in [gloss_key, var_key, "variant_morph-type"]:
        if key in entries:
            entries[key] = entries[key].apply(
                lambda x: [] if not isinstance(x, list) else x
            )

    entry_variants = {}

    def process_variant(entry, variant, var_count, idx):
        if variant["ID"] in var_dict:  # in theory, variants can have other variants
            for varvariant in var_dict[variant["ID"]]:
                log.warning(
                    f"The variant {entry_repr(variant['ID'])} of the entry {entry_repr(entry['ID'])} has the subvariant {entry_repr(varvariant['ID'])}. Is this accurate?"
                )
                var_count += 1
                if var_count < 10:  # stop recursion at some point
                    process_variant(entry, varvariant.copy(), var_count, idx)
        if variant["Gramm"] and variant["Gramm"] != entry["Gramm"]:
            log.warning(
                f"""The entry {entry_repr(variant["ID"])} is stored as a variant of {entry_repr(entry["ID"])}. It will not retain its part of speech."""
            )
        if gloss_key in variant and not pd.isnull(variant[gloss_key]):
            entry[gloss_key] = deduplicate(entry[gloss_key] + variant[gloss_key])
            if variant[gloss_key] != entry[gloss_key]:
                log.warning(
                    f"""The entry {entry_repr(entry["ID"])} is stored as having a different meaning than its variant {entry_repr(variant["ID"])}"""
                )
        else:
            variant[gloss_key] = entry.get(gloss_key, entry.get(definition_key, ""))
        variant["Parameter_ID"] = entry["Parameter_ID"]
        add_to_list_in_dict(entry_variants, entry["ID"], variant)

    def resolve_variants(entry):
        for idx, variant in enumerate(  # iterate gathered variants for this entry
            var_dict.get(entry["ID"], [])
        ):
            process_variant(
                entry=entry, variant=variant, var_count=len(entry["Variants"]), idx=idx
            )

    entries.apply(lambda x: resolve_variants(x), axis=1)

    # delete variants
    for col in entries.columns:
        if "variant-type" not in col:
            continue
        variants = entries[~(pd.isnull(entries[col]))]
        entries = entries.loc[~(entries.index.isin(variants.index))]

    # split up entries into lexemes, stems, morphemes, and morphs
    morphemes = entries[~(entries["Type"].isin(["phrase", "stem"]))]
    lexemes = entries[(entries["Type"].isin(["root", "stem"]))]

    def split_into_variants(rec, abstract_key, main_variant=None):
        for idx, (form, morph_type) in enumerate(
            zip(
                [rec["Form"]] + rec["Variants"],
                [rec["Type"]] + rec["variant_morph-type"],
            )
        ):
            new_rec = rec.copy()
            new_rec[abstract_key] = rec["ID"]
            new_rec["ID"] = rec["ID"] + f"-{idx}"
            new_rec["Form"] = form
            new_rec["Type"] = morph_type
            if main_variant:
                new_rec[main_variant] = rec["ID"] + "-0"
            yield dict(new_rec)
        for external_variant in entry_variants.get(rec["ID"], []):
            external_variant[abstract_key] = rec["ID"]
            if main_variant:
                external_variant[main_variant] = rec["ID"] + "-0"
            yield external_variant

    morphs = []
    stems = []
    morphemes.apply(
        lambda x: morphs.extend(split_into_variants(x, "Morpheme_ID")), axis=1
    )

    lexemes.apply(
        lambda x: stems.extend(
            split_into_variants(x, "Lexeme_ID", main_variant="Main_Stem")
        ),
        axis=1,
    )

    morphs = pd.DataFrame.from_dict(morphs)
    stems = pd.DataFrame.from_dict(stems)
    stems = stems[(stems["Type"].isin(["root", "stem"]))]

    sentence_path = Path(output_dir / "sentences.csv")
    ref_pattern = re.compile(r"^(\d+.\d)+$")
    if dictionary_examples:
        if sentence_path.is_file():
            log.info(
                f"Found {sentence_path.resolve()}, adding segmentation to examples"
            )
            glossed_examples = pd.read_csv(
                sentence_path, dtype=str, keep_default_na=False
            )
            juicy_columns = ["Analyzed_Word", "Gloss"]
            glossed_examples.dropna(subset=juicy_columns, inplace=True)
            for col in juicy_columns:
                glossed_examples = listify(glossed_examples, col, "\t")
            enriched_examples = []
            for ex in dictionary_examples:
                successful = False
                if " " in ex["source"]:
                    text_id, phrase_rec = ex["source"].split(" ")
                    if ref_pattern.match(phrase_rec):
                        rec, subrec = phrase_rec.split(".")
                        if subrec == "1":
                            subrec = ""
                        cands = glossed_examples[
                            (glossed_examples["Record_Number"] == rec)
                            & (glossed_examples["Phrase_Number"] == subrec)
                            & glossed_examples["Text_ID"].str.contains(text_id)
                        ]
                        if len(cands) == 1:
                            successful = True
                            enriched_examples.append(dict(cands.iloc[0]))
                        elif len(cands) > 1:
                            log.error(
                                f"Could not resolve ambiguous example reference [{text_id} {phrase_rec}]\n"
                                + cands.to_string()
                            )
                        else:
                            log.warning(
                                f"Could not resolve example reference [{text_id} {phrase_rec}]"
                            )
                if not successful:
                    enriched_examples.append(ex)
            dictionary_examples = pd.DataFrame.from_dict(enriched_examples)
        else:
            log.warning(
                f"There are dictionary examples. If you want to retrieve segmentation and glosses from the corpus, run cldflex flex2csv <your_file>.flextext and place sentences.csv in {output_dir.resolve()}"
            )
            dictionary_examples = pd.DataFrame.from_dict(dictionary_examples)
    else:
        dictionary_examples = pd.DataFrame.from_dict(dictionary_examples)

    dictionary_examples.fillna("", inplace=True)

    glottocode = conf.get("Glottocode", conf.get("Language_ID", None))
    with pd.option_context("mode.chained_assignment", None):
        if glottocode:
            for df in [entries, morphemes, morphs, dictionary_examples]:
                df["Language_ID"] = glottocode
        else:
            for df in [entries, morphemes, morphs, dictionary_examples]:
                df["Language_ID"] = obj_lg

    for df, name in [
        (entries, "entries"),
        (stems, "stems"),
        (lexemes, "lexemes"),
        (morphs, "morphs"),
        (morphemes, "morphemes"),
        (senses, "senses"),
    ]:
        df = delistify(df, sep)
        df.to_csv(output_dir / f"{name}.csv", index=False)

    if cldf:
        cldf_settings = conf.get("cldf", {})
        metadata = cldf_settings.get("metadata", {})
        mode = cldf_settings.get("lexicon", "dictionary")
        if mode == "wordlist":
            create_wordlist_dataset(
                forms=entries,
                senses=senses,
                glottocode=glottocode,
                metadata=metadata,
                output_dir=output_dir,
                cwd=lift_file.parents[0],
                sep=sep,
                parameters=cldf_settings.get("parameters", "multi"),
            )
        elif mode == "dictionary":
            if cldf_settings.get("drop_empty", False):
                senses = senses[senses["Description"] != ""]
            senses = senses[senses["Entry_ID"].isin(entries["ID"].values)]
            create_dictionary_dataset(
                entries,
                senses,
                metadata=metadata,
                examples=dictionary_examples,
                glottocode=glottocode,
                output_dir=output_dir,
                cwd=lift_file.parents[0],
            )
        elif mode == "rich":
            tables = {}
            with pd.option_context("mode.chained_assignment", None):
                for namedf in [morphs, lexemes, morphemes, stems]:
                    namedf.rename(columns={"Form": "Name"}, inplace=True)

            for name, df in [
                ("morphemes", morphemes),
                ("morphs", morphs),
                ("lexemes", lexemes),
                ("stems", stems),
                ("senses", senses),
            ]:
                if len(df) > 0:
                    tables[name] = df
            create_rich_dataset(
                tables=tables,
                glottocode=glottocode,
                metadata=metadata,
                output_dir=output_dir,
                cwd=lift_file.parents[0],
                sep=sep,
                parameters=cldf_settings.get("parameters", "multi"),
            )
        else:
            raise ValueError(mode)

    return morphs
