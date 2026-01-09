import nibabel as nib
import matplotlib.pyplot as plt
import numpy as np

img_path = "/root/autodl-tmp/data/Training/Labeled/A0S9V9/A0S9V9_sa.nii.gz"
gt_path  = "/root/autodl-tmp/data/Training/Labeled/A0S9V9/A0S9V9_sa_gt.nii.gz"

img = nib.load(img_path).get_fdata()
gt  = nib.load(gt_path).get_fdata()

print("img shape:", img.shape, "dtype:", img.dtype)
print("gt  shape:", gt.shape,  "dtype:", gt.dtype)

# 选中间 slice 和中间 time
s = img.shape[2] // 2
t = img.shape[3] // 2

img2d = img[:, :, s, t]
gt2d  = gt[:, :, s, t]

# 显示更清楚：用百分位裁剪灰度
vmin, vmax = np.percentile(img2d, (1, 99))

plt.figure(figsize=(12,4))

plt.subplot(1,3,1)
plt.imshow(img2d, cmap="gray", vmin=vmin, vmax=vmax)
plt.title(f"Image (slice={s}, time={t})")
plt.axis("off")

plt.subplot(1,3,2)
plt.imshow(gt2d)
plt.title("GT Mask")
plt.axis("off")

plt.subplot(1,3,3)
plt.imshow(img2d, cmap="gray", vmin=vmin, vmax=vmax)
plt.imshow(gt2d, alpha=0.4)
plt.title("Overlay")
plt.axis("off")

plt.tight_layout()

# 如果你是在无GUI环境，保存图片更稳
out_path = "/root/autodl-tmp/overlay.png"
plt.savefig(out_path, dpi=200)
print("Saved:", out_path)
print("Unique labels in this slice:", np.unique(gt2d))
