#exp_001_watchpicture

Date: 2026-01-09

##目的

使用watchpicture可视化部分结果

##Script
-src/watchpicture
##Outputs/fitures
-cat > experiment/exp_001_watchpicture/README.md << 'EOF'
#exp_001_watchpicture

##目的
-使用watchpicture可视化部分结果

##Script
-src/watchpicture

##Outputs
-figures/watchpicture

##Notes
-创立AutoDL与git仓库连接，在git保存管理项目
-.nii.gz Cine MRI短轴图像 gt.nii.gz Ground Truth分割 
-挑选一个数据/Training/Labeled/A0S9V9，可视化检测


## 项目结构
-project/
-├── src/                 # 训练/推理/后处理代码
-├── notes/               # Markdown 实验日志/问题记录
-├── experiments/         # 每次实验的配置快照 + 指标（推荐放 Git）
-├── figures/             # 论文最终用图（放 Git）
-└── outputs/             # 大量运行产物（默认不进 Git；可挑关键产出复制到 experiments/）

## 创建readme
-cat > experiment/exp_001_watchpicture/README.md << 'EOF'

## git提交
-cd ~/autodl-tmp/project
-git add src figures notes experiment
-git commit -m "exp_xxx: 你这次做了什么"
-git push

