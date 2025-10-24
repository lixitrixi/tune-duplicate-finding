import pandas as pd
import sys

from pyabc import Tune
import editdistance

# Edit distance between melodies in order to be considered the same
EDIT_DISTANCE_THRESHOLD = 4


def try_abc_to_tune(abc):
    try:
        return Tune(abc=abc)
    except:
        return None


def tune_to_notes_string(tune: Tune) -> str:
    return "".join(map(lambda n: n.note, tune.notes))


def main():
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    df = pd.read_excel(input_file)
    print(f"{len(df)} tunes loaded")

    # Parse ABC values into Tune objects for better analysis
    print(f"Parsing tune notation...")
    df["tune_obj"] = df["notation"].apply(try_abc_to_tune)

    # Prune failed rows (possibly invalid ABC) and sort descending by downloads
    df = df[df["tune_obj"].notna()]
    df.sort_values("downloaded", ascending=False, inplace=True)
    df.reset_index(inplace=True, drop=True)
    print(f"{len(df)} tunes parsed")

    # Turn notes into string representation for easy comparison
    df["notes_str"] = df["tune_obj"].apply(tune_to_notes_string)
    df["notes_len"] = df["notes_str"].apply(len)

    df["duplicate_group"] = pd.NA

    # Go through tunes and assign each to an existing or new "duplicate group"
    # Tunes get the same value for this column iff they are the same
    group_counter = 0
    for i, row in df.iterrows():
        print(f"...{i}/{len(df)} tunes processed", end="\r")
        # Already processed tunes
        candidates = df.iloc[0:i]

        # Remove obvious non-candidates (i.e. diff. time/key signature, lengths)
        candidates = candidates[(candidates["time_sig"] == row["time_sig"])]
        candidates = candidates[(candidates["key_sig"] == row["key_sig"])]
        candidates = candidates[candidates["notes_len"] == row["notes_len"]]

        edit_dist_func = lambda s: editdistance.distance(s, row["notes_str"])
        candidates["edit_dist"] = candidates["notes_str"].apply(edit_dist_func)
        candidates = candidates[candidates["edit_dist"] <= EDIT_DISTANCE_THRESHOLD]

        if candidates.empty:
            df.at[i, "duplicate_group"] = group_counter
            group_counter += 1
        else:
            df.at[i, "duplicate_group"] = candidates.iloc[0]["duplicate_group"]

    num_duplicates = len(df) - df.iloc[-1]["duplicate_group"]
    print(f"\nFound {num_duplicates} duplicates")

    df[["id", "title", "duplicate_group"]].to_csv(output_file)
    print(f"Wrote to {output_file}")


if __name__ == "__main__":
    main()
