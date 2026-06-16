import time
import os
import pandas as pd

from llm_processor import generate_product_json
from json_repair import repair_json
from state_manager import cancel_flags
from refinement import refine_product

os.makedirs("data/outputs", exist_ok=True)


# -----------------------------
# Simulated live market price
# -----------------------------
def get_live_market_price(base=100):
    import random
    return base * random.uniform(0.85, 1.20)


def process_job(tracking_id, job_status):

    file_path = job_status[tracking_id]["file_path"]
    df = pd.read_csv(file_path)
    total_rows = len(df)

    processed_results = []
    quarantined_rows = []

    # -----------------------------
    # INIT SAFE STATE (Layer 3 improvement)
    # -----------------------------
    job_status[tracking_id].setdefault("alerts", 0)
    job_status[tracking_id].setdefault("retry_count", 0)
    job_status[tracking_id].setdefault("last_updated", time.time())

    job_status[tracking_id]["status"] = "processing"

    for index, row in df.iterrows():

        # -----------------------------
        # STATE COLLISION CHECK (IMPROVED)
        # -----------------------------
        if cancel_flags.get(tracking_id, False):
            job_status[tracking_id]["status"] = "cancelled"
            job_status[tracking_id]["last_updated"] = time.time()
            return

        time.sleep(1.5)

        # -----------------------------
        # LLM CALL + JSON REPAIR (Layer 1)
        # -----------------------------
        raw_result = generate_product_json(row["product_description"])
        result = repair_json(raw_result)

        result.setdefault("estimated_unit_price", 0)
        result.setdefault("confidence_score", 0)
        result.setdefault("standardized_category", "Unknown")

        try:
            llm_price = float(result["estimated_unit_price"])
        except:
            llm_price = 0

        try:
            confidence = float(result["confidence_score"])
        except:
            confidence = 0

        # -----------------------------
        # LIVE MARKET PRICE (Layer 2 core)
        # -----------------------------
        market_price = get_live_market_price(100)

        variance = abs(llm_price - market_price) / market_price * 100

        result["variance"] = round(variance, 2)
        result["description"] = row["product_description"]
        result["live_market_price"] = round(market_price, 2)

        # -----------------------------
        # AUDIT ENGINE (CORRECTED LOGIC)
        # -----------------------------
        if variance > 15 or confidence < 85:

            job_status[tracking_id]["rows_quarantined"] += 1
            job_status[tracking_id]["alerts"] += 1

            # refinement loop
            refined_result = refine_product(result)
            refined_result["retry_applied"] = True

            quarantined_rows.append(refined_result)

        else:
            processed_results.append(result)

        # -----------------------------
        # PROGRESS + SAFE STATE UPDATE
        # -----------------------------
        processed_rows = index + 1
        job_status[tracking_id]["progress"] = int((processed_rows / total_rows) * 100)
        job_status[tracking_id]["rows_processed"] = processed_rows

        # cost tracking (safe incremental)
        job_status[tracking_id]["estimated_cost"] += 0.0012

        # timestamp update (IMPORTANT for audit traceability)
        job_status[tracking_id]["last_updated"] = time.time()

    # -----------------------------
    # SAVE OUTPUTS
    # -----------------------------
    if processed_results:
        pd.DataFrame(processed_results).to_csv(
            f"data/outputs/{tracking_id}_results.csv",
            index=False
        )

    if quarantined_rows:
        pd.DataFrame(quarantined_rows).to_csv(
            f"data/outputs/{tracking_id}_quarantine.csv",
            index=False
        )

    # -----------------------------
    # FINAL STATE
    # -----------------------------
    job_status[tracking_id]["status"] = "completed"
    job_status[tracking_id]["progress"] = 100
    job_status[tracking_id]["last_updated"] = time.time()