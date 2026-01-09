## nnU-Net v2
-医学分割自动化流程
## convert_mms_to_nnunet.py
-数据格式转换
  -将所有病例分布到一个目录
  -给图像文件加上模态数_0000
  -将GT放到labelsTr/
  -自动生成dataset.json，告诉nnU-Net：有几个模态、label各自代表什么、文件后缀是什么
## 3d_to_4d.py
-nnU-Net无法识别4D图像（H,W,S,T）（图像像素高，图像像素宽，短轴方向切片数，心动周期时相数），需将其转化为3D图像在进行预处理
