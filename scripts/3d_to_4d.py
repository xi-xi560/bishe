import json
import shutil
from pathlib import Path
import nibabel as nib
import numpy as np

SRC = Path("/root/autodl-tmp/data/Training/Labeled")
DST_BASE = Path("/root/autodl-tmp/nnUNet_raw")
DATASET_NAME = "Dataset002_MMs_Cine3D"   # 新数据集，避免覆盖
DST = DST_BASE / DATASET_NAME
imagesTr = DST / "imagesTr"
labelsTr = DST / "labelsTr"
imagesTr.mkdir(parents=True, exist_ok=True)
labelsTr.mkdir(parents=True, exist_ok=True)

cases = sorted([p for p in SRC.iterdir() if p.is_dir()])
if len(cases) == 0:
    raise RuntimeError(f"No case folders found in {SRC}")

num_cases = 0
num_samples = 0

for case_dir in cases:
    case_id = case_dir.name
    img_path = case_dir / f"{case_id}_sa.nii.gz"
    gt_path  = case_dir / f"{case_id}_sa_gt.nii.gz"
    if not img_path.exists() or not gt_path.exists():
        print(f"[SKIP] missing img/gt for {case_id}")
        continue

    img_nii = nib.load(str(img_path))
    gt_nii  = nib.load(str(gt_path))
    img = img_nii.get_fdata()
    gt  = gt_nii.get_fdata()

    # 期望 4D: (H, W, S, T)
    if img.ndim != 4 or gt.ndim != 4:
        raise RuntimeError(f"{case_id}: expected 4D (H,W,S,T), got img {img.shape}, gt {gt.shape}")
    if img.shape != gt.shape:
        raise RuntimeError(f"{case_id}: img/gt shape mismatch: {img.shape} vs {gt.shape}")

    H,W,S,T = img.shape
    # 每个 time frame 生成一个 3D 样本 (H,W,S)
    # nnU-Net: 单模态图像命名 *_0000.nii.gz；label 同名无 _0000
    for t in range(T):
        sample_id = f"{case_id}_t{t:02d}"
        out_img = imagesTr / f"{sample_id}_0000.nii.gz"
        out_gt  = labelsTr / f"{sample_id}.nii.gz"

        img_t = img[:, :, :, t].astype(np.float32)
        gt_t  = gt[:, :, :, t].astype(np.uint8)

        nib.save(nib.Nifti1Image(img_t, img_nii.affine, img_nii.header), str(out_img))
        nib.save(nib.Nifti1Image(gt_t,  gt_nii.affine,  gt_nii.header),  str(out_gt))
        num_samples += 1

    num_cases += 1
    if num_cases % 10 == 0:
        print(f"Processed {num_cases} cases... total samples so far: {num_samples}")

print(f"Done. cases={num_cases}, samples={num_samples}")
print("Dataset at:", DST)

dataset_json = {
    "channel_names": {"0": "cine_sa"},
    "labels": {
        "background": 0,
        "LV_cavity": 1,
        "LV_myo": 2,
        "RV_cavity": 3
    },
    "numTraining": num_samples,
    "file_ending": ".nii.gz"
}
with open(DST / "dataset.json", "w", encoding="utf-8") as f:
    json.dump(dataset_json, f, indent=2, ensure_ascii=False)
print("Wrote:", DST / "dataset.json")