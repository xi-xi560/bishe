import json
import shutil
from pathlib import Path

SRC = Path("/root/autodl-tmp/data/Training/Labeled")
DST_BASE = Path("/root/autodl-tmp/nnUNet_raw")
DATASET_NAME = "Dataset001_MMs"

DST = DST_BASE / DATASET_NAME
imagesTr = DST / "imagesTr"
labelsTr = DST / "labelsTr"

imagesTr.mkdir(parents=True, exist_ok=True)
labelsTr.mkdir(parents=True, exist_ok=True)

cases = sorted([p for p in SRC.iterdir() if p.is_dir()])
if len(cases) == 0:
    raise RuntimeError(f"No case folders found in {SRC}")

num_copied = 0
for case_dir in cases:
    case_id = case_dir.name
    img_path = case_dir / f"{case_id}_sa.nii.gz"
    gt_path  = case_dir / f"{case_id}_sa_gt.nii.gz"

    if not img_path.exists():
        print(f"[SKIP] missing image: {img_path}")
        continue
    if not gt_path.exists():
        print(f"[SKIP] missing label: {gt_path}")
        continue

    out_img = imagesTr / f"{case_id}_0000.nii.gz"
    out_gt  = labelsTr / f"{case_id}.nii.gz"

    shutil.copyfile(img_path, out_img)
    shutil.copyfile(gt_path, out_gt)
    num_copied += 1

print(f"Copied {num_copied} cases to {DST}")

dataset_json = {
    "channel_names": {"0": "cine_sa"},
    "labels": {
        "background": 0,
        "LV_cavity": 1,
        "LV_myo": 2,
        "RV_cavity": 3
    },
    "numTraining": num_copied,
    "file_ending": ".nii.gz"
}

with open(DST / "dataset.json", "w", encoding="utf-8") as f:
    json.dump(dataset_json, f, indent=2, ensure_ascii=False)

print("Wrote:", DST / "dataset.json")
