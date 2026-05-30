import csv
import math
import random
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path


CSV_PATH = Path("data/products_price.csv")
RANDOM_SEED = 20260530


def parse_price(price_text: str) -> float:
    return float(price_text.replace("$", "").replace(",", ""))


def price_text(value: float) -> str:
    return f"${value:.2f}"


def main() -> None:
    random.seed(RANDOM_SEED)

    with CSV_PATH.open("r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    # Prevent duplicate generation if years are already present.
    years_present = {datetime.strptime(r["DATE"], "%m/%d/%Y").year for r in rows}
    missing_years = [y for y in (2024, 2023) if y not in years_present]
    if not missing_years:
        print("No changes made: 2023 and 2024 already exist.")
        return

    base_2025 = [r for r in rows if datetime.strptime(r["DATE"], "%m/%d/%Y").year == 2025]
    by_product = defaultdict(list)
    for r in base_2025:
        by_product[r["PRODUCT_ID"]].append(r)

    for pid in by_product:
        by_product[pid].sort(key=lambda r: datetime.strptime(r["DATE"], "%m/%d/%Y"))

    # Base price: first day (01/01/2025) price for each product.
    base_price = {pid: parse_price(entries[0]["PRODUCT_PRICE"]) for pid, entries in by_product.items()}

    # Detect 2025 outliers (approx 30%+ lower than base).
    outlier_mmdd = {}
    for pid, entries in by_product.items():
        b = base_price[pid]
        outlier_mmdd[pid] = {
            datetime.strptime(r["DATE"], "%m/%d/%Y").strftime("%m/%d")
            for r in entries
            if parse_price(r["PRODUCT_PRICE"]) <= b * 0.72
        }

    month_factor = {
        2024: {1: 0.99, 2: 1.01, 3: 1.04, 4: 0.98, 5: 1.00, 6: 1.02},
        2023: {1: 1.02, 2: 0.98, 3: 1.00, 4: 1.03, 5: 0.97, 6: 0.99},
    }

    new_rows = []
    for target_year in missing_years:
        jan1 = datetime(target_year, 1, 1)
        jun30 = datetime(target_year, 6, 30)

        shifted_outliers = {}
        for pid, mmdd_set in outlier_mmdd.items():
            shifted = set()
            for mmdd in mmdd_set:
                base_day = datetime.strptime(f"{mmdd}/{target_year}", "%m/%d/%Y")

                direction = 1 if target_year == 2024 else -1
                if random.random() < 0.30:
                    direction *= -1

                sale_day_1 = base_day + timedelta(days=direction)
                if jan1 <= sale_day_1 <= jun30:
                    shifted.add(sale_day_1.strftime("%m/%d"))

                # Sometimes make it a 2-day promo to simulate sale weekend.
                if random.random() < 0.45:
                    sale_day_2 = sale_day_1 + timedelta(days=direction)
                    if jan1 <= sale_day_2 <= jun30:
                        shifted.add(sale_day_2.strftime("%m/%d"))

            shifted_outliers[pid] = shifted

        for row in base_2025:
            source_date = datetime.strptime(row["DATE"], "%m/%d/%Y")
            target_date = datetime(target_year, source_date.month, source_date.day)
            pid = row["PRODUCT_ID"]
            b = base_price[pid]
            source_price = parse_price(row["PRODUCT_PRICE"])
            mmdd = target_date.strftime("%m/%d")

            if mmdd in shifted_outliers[pid]:
                # Discount outlier around 30% to 35% from base.
                discount = random.uniform(0.30, 0.35)
                p = b * (1.0 - discount)
            else:
                # Keep some days unchanged and vary others to create realistic periods.
                if random.random() < 0.35:
                    p = source_price
                else:
                    wave_phase = 0.7 if target_year == 2024 else 1.8
                    wave = 1.0 + 0.04 * math.sin((2.0 * math.pi * target_date.timetuple().tm_yday / 30.0) + wave_phase)
                    noise = 1.0 + random.uniform(-0.03, 0.03)
                    candidate = b * month_factor[target_year][target_date.month] * wave * noise
                    p = 0.55 * source_price + 0.45 * candidate

                # Clamp regular days to +/-25% from base.
                p = max(b * 0.75, min(b * 1.25, p))

            new_rows.append(
                {
                    "PRODUCT_ID": row["PRODUCT_ID"],
                    "PRODUCT_DESCRIPTION": row["PRODUCT_DESCRIPTION"],
                    "PRODUCT_PRICE": price_text(round(p, 2)),
                    "DATE": target_date.strftime("%m/%d/%Y"),
                }
            )

    all_rows = rows + new_rows
    headers = ["PRODUCT_ID", "PRODUCT_DESCRIPTION", "PRODUCT_PRICE", "DATE"]
    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"Added rows: {len(new_rows)}")
    print(f"Total rows: {len(all_rows)}")


if __name__ == "__main__":
    main()
