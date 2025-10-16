import io
import math
import re

import pandas as pd
import pdfplumber


def _split_and_remove_spaces(text: str) -> str:
    # there is always a blank line between consecutive entries
    # while a single entry can be on two consecutive lines
    text = re.split(r"^ *\n", text, flags=re.MULTILINE)
    # remove extra whitespace
    text = [
        re.sub(r"\s{3,}", " ", t.strip()).replace("  ", " ") for t in text if t.strip()
    ]
    return text


def postprocess_teams(text: str) -> list[str]:
    # remove subheaders such "1 Giornata di Andata"
    text = re.sub(r"^.*Giornata di.*$", "", text, flags=re.MULTILINE | re.IGNORECASE)

    teams = _split_and_remove_spaces(text)
    # if there are two digits in subheader such as "10 Giornata di ..."
    # one of the digit may be caught inside the team column,
    # so we remove it
    teams = [t for t in teams if re.sub(r"\d+", "", t)]

    return teams


def postprocess_date_time(text: str) -> list[tuple[str, str]]:
    # there is always a blank line between consecutive entries
    text = _split_and_remove_spaces(text)
    # split date (DD/MM/YYYY) and time (HH:MM) using spaces between them
    dt = [re.split(r" +", t.strip()) for t in text if t.strip()]
    return dt


def postprocess_address(text: str) -> list[tuple[str, str]]:
    # there is always a blank line between consecutive entries
    text = _split_and_remove_spaces(text)
    # get court name and address using the first '-' as separator
    # (optionally with white space around it)
    address = [
        re.split(r" *- *", t, maxsplit=1) for t in text if "note" not in t.lower()
    ]
    return address


def parse_pdf(file: io.BytesIO) -> pd.DataFrame:
    pdf = pdfplumber.open(file)
    first_page = pdf.pages[0]

    HEADER_BOTTOM = math.ceil(first_page.search("Gara N", case=False)[0]["bottom"])
    SQUADRA_A_LEFT = math.floor(first_page.search("Squadra A", case=False)[0]["x0"])
    SQUADRA_B_LEFT = math.floor(first_page.search("Squadra B", case=False)[0]["x0"])
    GIORNO_LEFT = math.floor(first_page.search("Giorno", case=False)[0]["x0"])
    GIORNO_RIGHT = math.ceil(first_page.search("Giorno", case=False)[0]["x1"])

    def _filter_exclude_header(obj):
        return obj["bottom"] > HEADER_BOTTOM

    def _filter_bold_chars(obj):
        return "bold" in obj["fontname"].lower()

    # def num_gara(obj):
    #     return obj["x0"] < 88

    def _filter_squadra_a(obj):
        return (
            _filter_exclude_header(obj)
            and _filter_bold_chars(obj)
            and (obj["x0"] > SQUADRA_A_LEFT)
            and (obj["x1"] < SQUADRA_B_LEFT)
        )

    def _filter_squadra_b(obj):
        return (
            _filter_exclude_header(obj)
            and _filter_bold_chars(obj)
            and (obj["x0"] > SQUADRA_B_LEFT)
            and (obj["x1"] < GIORNO_LEFT)
        )

    def _filter_date_time(obj):
        return (
            _filter_exclude_header(obj)
            and _filter_bold_chars(obj)
            and obj["x0"] > GIORNO_RIGHT
        )

    def _filter_address(obj):
        return _filter_exclude_header(obj) and not _filter_bold_chars(obj)

    filters_func = {
        "squadra_a": _filter_squadra_a,
        "squadra_b": _filter_squadra_b,
        "date_time": _filter_date_time,
        "address": _filter_address,
    }

    postprocess_func = {
        "squadra_a": postprocess_teams,
        "squadra_b": postprocess_teams,
        "date_time": postprocess_date_time,
        "address": postprocess_address,
    }

    result = {
        "squadra_a": "",
        "squadra_b": "",
        "date_time": "",
        "address": "",
    }

    for page in pdf.pages[:]:
        for k in result.keys():
            filter_page = page.filter(lambda obj: filters_func[k](obj))
            text = filter_page.extract_text(layout=True, use_text_flow=False)
            result[k] += f"\n{text}"

    for k, v in result.items():
        result[k] = postprocess_func[k](v)

    # check if all have same length
    tot = [len(v) for v in result.values()]
    N = tot[0]
    if not all([t == N for t in tot]):
        print("Error: found different number of entries")
        for k, v in result.items():
            print(f"  {k}: {len(v)}")
        raise ValueError("Different number of entries")

    df = []

    for i in range(N):
        df.append(
            {
                "Home": result["squadra_a"][i],
                "Away": result["squadra_b"][i],
                "Date": result["date_time"][i][0],
                "Time": result["date_time"][i][1],
                "Court": result["address"][i][0],
                "Address": result["address"][i][1],
            }
        )

    df = pd.DataFrame(df)

    return df
