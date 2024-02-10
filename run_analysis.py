"""
Runs analysis on a number of scans.
This is used to analyze a scan for the first or to re-analyze an existing scan.
"""

import time
from tqdm import tqdm
from api import Api

# Increase timeout for analysis since it can take a while!
api = Api(timeout=3 * 60)


def analyze(scan_id):
    """
    Analyzes the scan with the given ID
    """
    try:
        api.post(f"/analysis/{scan_id}/analyze/")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to analyze scan {scan_id}")
        print(e)
        return False


if __name__ == "__main__":
    scan_ids = input("Enter scan IDs separated by commas: ")
    start_time = time.time()
    # Clean the input
    scan_ids = [x.strip() for x in scan_ids.strip().split(",")]

    # Iterate through each scan
    progress_bar = tqdm(scan_ids, desc="Analyzing scans")

    failed_scans = []
    for scan_id in progress_bar:
        progress_bar.set_description(f"Analyzing scan {scan_id}")
        response = analyze(scan_id)
        if response is False:
            failed_scans.append(scan_id)

    # Done. Print some stats
    elapsed_time = time.time() - start_time
    print("=" * 50)
    print(f"Done in {elapsed_time:.2f} seconds")
    print(f"Succeeded {len(scan_ids) - len(failed_scans)}/{len(scan_ids)} scans")
    print(f"Failed {len(failed_scans)}/{len(scan_ids)} scans: {failed_scans}")
    print("=" * 50)
