import requests
from bs4 import BeautifulSoup
from tabulate import tabulate
from collections import Counter
from itertools import combinations
import random
from typing import List, Dict, Tuple, Optional

# --------------------- Config ---------------------
URL = "https://zh.lottolyzer.com/search/hong-kong/mark-six"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36",
    "Referer": "https://zh.lottolyzer.com/search/hong-kong/mark-six",
    "Origin": "https://zh.lottolyzer.com",
    "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
}


def get_all_records(last_draws: int = 10) -> List[Dict]:
    """
    Fetch the last N Mark Six draws and return structured data.
    
    Returns:
        List of dictionaries, each containing:
        {
            "draw_date": str,
            "winning_numbers": List[int],
            "extra_number": int,
            "repeated_from_last": List[int]
        }
    """
    payload = {
        "last": str(last_draws),
        "search": "search-by-last"
    }

    with requests.Session() as session:
        session.get("https://zh.lottolyzer.com/home/hong-kong/mark-six", headers=HEADERS)
        response = session.post(URL, data=payload, headers=HEADERS)
        response.raise_for_status()
        response.encoding = 'utf-8'

        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find("table", {"id": "summary-table"})
        
        if not table:
            raise ValueError("Cannot find results table - site structure may have changed.")

        rows = table.select("tbody tr")
        results = []

        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 5:
                continue

            winning_str = cols[2].get_text(strip=True)
            extra_str   = cols[3].get_text(strip=True)
            repeat_str  = cols[4].get_text(strip=True)

            winning_numbers = [int(x) for x in winning_str.split(",") if x.strip().isdigit()]
            extra_number = int(extra_str) if extra_str.strip().isdigit() else None
            repeated_numbers = [int(x) for x in repeat_str.split(",") if x.strip().isdigit()] if repeat_str else []

            results.append({
                "winning_numbers": winning_numbers,
                "extra_number": extra_number,
                "repeated_from_last": repeated_numbers
            })

        return results


def get_random_nums(records: List[Dict], k: int = 6) -> List[int]:
    """Generate random 6 numbers from the most repeated numbers in the records."""
    all_numbers = []
    for draw in records:
        all_numbers.extend(draw["winning_numbers"])
        if draw["extra_number"]:
            all_numbers.append(draw["extra_number"])

    counter = Counter(all_numbers)
    # Only numbers that appeared at least twice
    candidates = [num for num, count in counter.items() if count >= 2]
    
    if len(candidates) < k:
        # Fallback: use all numbers if not enough repeats
        candidates = list(counter.keys())
    
    selected = random.sample(candidates, k)
    return sorted(selected)


def get_repeat_numbers(records: List[Dict]) -> List[Tuple[int, int]]:
    """
    Return most repeated numbers with their frequencies.
    Format: [(number, times_appeared), ...] sorted by frequency descending
    """
    all_numbers = []
    for draw in records:
        all_numbers.extend(draw["winning_numbers"])
        if draw["extra_number"]:
            all_numbers.append(draw["extra_number"])

    counter = Counter(all_numbers)
    repeated = [(num, count) for num, count in counter.items() if count > 1]
    repeated.sort(key=lambda x: x[1], reverse=True)
    
    return repeated


def get_repeat_pairs(records: List[Dict], min_times: int = 2) -> List[Tuple[str, int]]:
    """
    Return most frequently appearing number pairs.
    Format: [("n1, n2", times_appeared), ...]
    """
    all_pairs = []
    for draw in records:
        numbers = draw["winning_numbers"].copy()
        if draw["extra_number"]:
            numbers.append(draw["extra_number"])
        
        for pair in combinations(sorted(numbers), 2):
            all_pairs.append(tuple(pair))

    pair_counter = Counter(all_pairs)
    frequent_pairs = [p for p in pair_counter.most_common() if p[1] >= min_times]

    # Convert to nice display format
    result = []
    for (n1, n2), count in frequent_pairs:
        result.append((f"{n1}, {n2}", count))

    return result


# --------------------- Main Usage Example ---------------------
if __name__ == "__main__":
    last_n = int(input('How many last draws do you want? (1-20) : ').strip())
    # Main functions
    records = get_all_records(last_n)

    random_numbers = get_random_nums(records)
    repeated_nums = get_repeat_numbers(records)
    repeated_pairs = get_repeat_pairs(records)

    # --------------------- Display Results ---------------------
    print("=== Last Draws ===")
    table_data = []
    for r in records:
        table_data.append([
            ", ".join(map(str, r["winning_numbers"])),
            r["extra_number"],
            ", ".join(map(str, r["repeated_from_last"])) if r["repeated_from_last"] else "-"
        ])
    
    print(tabulate(table_data, 
                   headers=["Winning Numbers", "Extra Number", "Repeated from Last"], 
                   tablefmt="grid"))

    print("\n=== Suggested Random Numbers (from hot numbers) ===")
    print(random_numbers)

    print("\n=== Most Repeated Numbers ===")
    print(tabulate(repeated_nums, headers=["Number", "Times Appeared"], tablefmt="grid"))

    print("\n=== Most Frequently Appearing Number Pairs ===")
    if repeated_pairs:
        print(tabulate(repeated_pairs, headers=["Number Pair", "Times Appeared Together"], tablefmt="grid"))
    else:
        print("No pairs appeared more than once in the selected draws.")
