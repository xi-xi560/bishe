import json
import re
import shutil
from pathlib import Path

import nibabel as nib
import numpy as np

SRC = Path("/root/autodl-tmp/nnUNet_raw/Dataset002_MMs_Cine3D")
DST = Path("/root/autodl-tmp/nnUNet_raw/Dataset003_MMs_EDES")

imagesTr_src = SRC / "imagesTr"
labelsTr_src = SRC / "labelsTr"
imagesTr_dst = DST / "imagesTr"
labelsTr_dst = DST / "labelsTr"
imagesTr_dst.mkdir(parents=True, exist_ok=True)
labelsTr_dst.mkdir(parents=True, exist_ok=True)

# labels 名称应为 PID_tXX.nii.gz
pat = re.compile(r"^(?P<pid>[A-Z0-9]+)_t(?P<t>\d{2})$")

by_pid = {}
for lbl in sorted(labelsTr_src.glob("*.nii.gz")):
    stem = lbl.name.replace(".nii.gz", "")
    m = pat.match(stem)
    if not m:
        continue
    pid = m.group("pid")
    t = int(m.group("t"))
    by_pid.setdefault(pid, []).append((t, lbl))

if not by_pid:
    raise RuntimeError(f"No labels found in {labelsTr_src}. Expected names like PID_tXX.nii.gz")

def lv_volume_ml(label_nii_path: Path) -> float:
    nii = nib.load(str(label_nii_path))
    data = nii.get_fdata()
    lv = (data == 1)  # LV cavity label=1
    vox = int(np.count_nonzero(lv))
    zooms = nii.header.get_zooms()[:3]  # mm
    v_mm3 = float(zooms[0] * zooms[1] * zooms[2])
    return vox * v_mm3 / 1000.0  # mL

selected = []  # (pid, ed_t, es_t)
copied = 0

for pid, items in sorted(by_pid.items()):
    vols = []
    for t, lbl_path in items:
        try:
            v = lv_volume_ml(lbl_path)
        except Exception as e:
            print(f"[WARN] {pid}_t{t:02d}: cannot read label ({e}), skip")
            continue
        vols.append((t, v))
    if len(vols) < 2:
        print(f"[SKIP] {pid}: not enough valid frames")
        continue

    vols_sorted = sorted(vols, key=lambda x: x[1])
    es_t, es_v = vols_sorted[0]
    ed_t, ed_v = vols_sorted[-1]

    # 如果 ES 为 0（极少数标注缺失情况），选最小的非零
    if es_v == 0:
        nz = [x for x in vols_sorted if x[1] > 0]
        if nz:
            es_t, es_v = nz[0]

    selected.append((pid, ed_t, es_t))

    for tag, t_sel in [("ED", ed_t), ("ES", es_t)]:
        sample_id = f"{pid}_{tag}"
        img_src = imagesTr_src / f"{pid}_t{t_sel:02d}_0000.nii.gz"
        lbl_src = labelsTr_src / f"{pid}_t{t_sel:02d}.nii.gz"
        if not img_src.exists() or not lbl_src.exists():
            print(f"[WARN] Missing image/label for {pid} t{t_sel:02d}, skip {tag}")
            continue
        shutil.copyfile(img_src, imagesTr_dst / f"{sample_id}_0000.nii.gz")
        shutil.copyfile(lbl_src, labelsTr_dst / f"{sample_id}.nii.gz")
        copied += 1

print(f"Selected ED/ES for {len(selected)} patients. Copied files: {copied}.")
print("Dataset003 at:", DST)

dataset_json = {
    "channel_names": {"0": "cine_sa"},
    "labels": {"background": 0, "LV_cavity": 1, "LV_myo": 2, "RV_cavity": 3},
    "numTraining": len(list(labelsTr_dst.glob("*.nii.gz"))),
    "file_ending": ".nii.gz"
}
with open(DST / "dataset.json", "w", encoding="utf-8") as f:
    json.dump(dataset_json, f, indent=2, ensure_ascii=False)

with open(DST / "selected_frames.txt", "w", encoding="utf-8") as f:
    for pid, ed_t, es_t in selected:
        f.write(f"{pid}\tED=t{ed_t:02d}\tES=t{es_t:02d}\n")

print("Wrote:", DST / "dataset.json")
print("Wrote:", DST / "selected_frames.txt")