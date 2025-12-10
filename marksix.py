import requests
from bs4 import BeautifulSoup
from tabulate import tabulate
from collections import Counter
from itertools import combinations
import random

# --------------------- Config ---------------------
URL = "https://zh.lottolyzer.com/search/hong-kong/mark-six"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36",
    "Referer": "https://zh.lottolyzer.com/search/hong-kong/mark-six",
    "Origin": "https://zh.lottolyzer.com",
    "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
}

LAST_DRAWS = input('How many last draws do you want? (10, 20, 50, 100) : ');
# --------------------------------------------------

payload = {
    "last": str(LAST_DRAWS),
    "search": "search-by-last"
}

with requests.Session() as session:
    session.get("https://zh.lottolyzer.com/home/hong-kong/mark-six", headers=HEADERS)

    response = session.post(URL, data=payload, headers=HEADERS)
    response.raise_for_status()
    response.encoding = 'utf-8'

    soup = BeautifulSoup(response.text, 'html.parser')

# Find the results table
table = soup.find("table", {"id": "summary-table"})
if not table:
    raise ValueError("Cannot find results table - site may have changed")

rows = table.select("tbody tr")

results = []
for row in rows:
    cols = row.find_all("td")

    winning_str = cols[2].get_text(strip=True)
    extra_str   = cols[3].get_text(strip=True)
    repeat_str  = cols[4].get_text(strip=True)

    # Convert to lists of integers
    winning_numbers = [int(x) for x in winning_str.split(",") if x.isdigit()]
    extra_number   = int(extra_str) if extra_str.isdigit() else None
    repeated_numbers = [int(x) for x in repeat_str.split(",") if x.isdigit()] if repeat_str else []

    results.append({
        "winning_numbers": winning_numbers,
        "extra_number": extra_number,
        "repeated_from_last": repeated_numbers
    })

# --------------------- Output ---------------------
# --------------------- Get Result ---------------------
headers = ["Winning Numbers", "Extra Number", "Repeated from Last"]

# Convert the data into rows
table_data = []
for r in results:
    table_data.append([
        ", ".join(map(str, r["winning_numbers"])),
        r["extra_number"],
        ", ".join(map(str, r["repeated_from_last"])) if r["repeated_from_last"] else "-"
    ])

# print(tabulate(table_data, headers=headers, tablefmt="grid"))

# --------------------- Most Repeated Numbers  ---------------------
all_numbers = []

for draw in results:
    all_numbers.extend(draw["winning_numbers"])
    all_numbers.append(draw["extra_number"])

counter = Counter(all_numbers)
repeated_numbers = {num: count for num, count in counter.items() if count > 1}
repeated_numbers_sorted = dict(sorted(repeated_numbers.items(), key=lambda x: x[1], reverse=True))

repeated_list = [(num, count) for num, count in repeated_numbers_sorted.items()]

repeated_headers = ["Number", "Times Appeared"]

# Random no.
can_drow_list = list(repeated_numbers.keys())
selected = random.sample(can_drow_list, 6)
selected_sorted = sorted(selected)
print("\n=== Random Number ===")
print(selected_sorted)


print("\n=== Most Repeated Numbers ===")
print(tabulate(repeated_list, headers=repeated_headers, tablefmt="grid"))

# --------------------- Most Frequently Appearing Number Pairs  ---------------------
all_pairs = []

for draw in results:
    numbers = draw["winning_numbers"] + [draw["extra_number"]]
    for pair in combinations(sorted(numbers), 2):
        all_pairs.append(tuple(pair))
pair_counter = Counter(all_pairs)
most_common_pairs = pair_counter.most_common()

frequent_pairs = [p for p in most_common_pairs if p[1] >= 2]

frequent_pairs.sort(key=lambda x: x[1], reverse=True)

pair_table = []
for (n1, n2), count in frequent_pairs:
    pair_table.append([f"{n1}, {n2}", count])

# pair_headers = ["Number Pair", "Times Appeared Together"]

# print("\n=== Most Frequently Appearing Number Pairs ===")
# if pair_table:
#     print(tabulate(pair_table, headers=pair_headers, tablefmt="grid"))
