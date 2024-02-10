"""
This script downloads the patch data from the server and saves it to a file.
It allows the user to specify which patient's scans to download.
Multiple scans of the same patient are saved to a single Excel file with multiple sheets corresponding to each scan.
"""

import io

import pandas as pd
from tqdm import tqdm

from api import Api

api = Api()


def get_patient_scans(patient_id):
    """
    Gets all the scans associated with this patient
    """
    print("Patient ID: ", patient_id)
    scans = api.get("/scan/search/", params={"patient__id": patient_id}).json()
    print(f"Found {len(scans)} scans")
    return scans


def get_patch_data(scan_id):
    try:
        file_to_download = "patch_data_*mm.csv"
        # Download the patch_data_*mm.csv file
        patch_data = api.get(f"/scan/{scan_id}/file/?path={file_to_download}").content
        return patch_data
    except Exception as e:
        print(f"[ERROR] Failed to download patch data for scan {scan_id}, skipping")
        print(e)
        return None


if __name__ == "__main__":
    patient_id = input("Enter patient ID: ").strip()
    patient_scans = get_patient_scans(patient_id)

    # Iterate through each scan and download the patch data
    all_patch_datas = []
    failed_scans = []
    for scan in tqdm(patient_scans):
        patch_data = get_patch_data(scan["id"])
        if patch_data is None:
            failed_scans.append(scan)
        else:
            all_patch_datas.append({"scan": scan, "patch_data": patch_data})

    # Use pandas to convert the list of CSVs into a single excel file with multiple sheets for each scan
    out_file = f"patient_{patient_id}_patch_data.xlsx"
    with pd.ExcelWriter(out_file, engine="openpyxl") as writer:
        for item in all_patch_datas:
            df = pd.read_csv(io.StringIO(item["patch_data"].decode("utf-8")))
            df.to_excel(writer, sheet_name=f"Scan {item['scan']['id']}")

    # Done. Print some stats
    print("=" * 50)
    print("Saved to", out_file)
    print(f"Succeeded {len(all_patch_datas)}/{len(patient_scans)} scans")
    print(
        f"Failed {len(failed_scans)}/{len(patient_scans)} scans: {[scan['id'] for scan in failed_scans]}"
    )
    print("=" * 50)
