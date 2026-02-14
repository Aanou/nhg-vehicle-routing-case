

# NHG Vehicle Routing Case Study 🚚📦

> **2026 IISE Logistics & Supply Chain Division Student Case Competition** > **Topic:** Growing Pains: A Case Study for Large-Scale Vehicle Routing

## 📖 项目简介 (Project Overview)

本项目旨在为 **Northeastern Home Goods (NHG)** 制定年度物流基准估算。针对 NHG 将配送业务外包给位于 **Wilmington, MA** 的第三方物流商 (MAD) 的场景，我们需要计算在维持现有“固定配送日”计划下的**年度总行驶里程 (Annual Total Miles)**。

该分析将作为评估外包报价公平性的基准模型 。

## 🎯 核心目标与约束 (Objectives & Constraints)

我们的目标是设计满足以下严格约束的车辆路径 (VRP)，并最小化总里程：

* **物理约束**:
* **车辆容量**: 最大 3,200  。


* **配送窗口**: 门店营业时间 8:00 A.M. - 6:00 P.M. 。

* **固定计划**: 同一线路只能包含同一天的订单 (No mixed days) 。




* **运营参数**:
* **行驶速度**: 40 mph (混合路况) 。


* **卸货时间**:  分钟 。




* **DOT 法规 (11/14 小时规则)**:


* 最大驾驶时间: 11 小时。
* 最大值勤时间: 14 小时 (包含驾驶、卸货、等待)。
* **跨夜逻辑 (Sleeper Cab)**: 若超出上述限制，必须强制休息 10 小时。



## 📂 项目结构 (Repository Structure)

```text
nhg-vehicle-routing-case/
├── data/                   # 原始数据 (Git ignored)
│   ├── orders.csv          # 订单需求 (OrderTable)
│   ├── locations.csv       # 门店位置 (LocationTable)
│   └── distances.csv       # 距离矩阵 (Distances)
├── notebooks/              # Jupyter Notebooks 分析
│   └── 01_exploratory_analysis.ipynb  # EDA: 每日货量统计、地图可视化、卸货时间分布
├── src/                    # 核心源代码
│   ├── data_loader.py      # 数据加载与预处理 (自动处理列名空格)
│   ├── utils.py            # 业务逻辑裁判 (计算卸货时间、DOT法规校验)
│   └── model.py            # [TODO] 路径优化算法 (Savings Algorithm)
├── results/                # 输出结果与图表
├── requirements.txt        # Python 依赖
└── README.md               # 项目文档

```

## 🚀 快速开始 (Getting Started)

### 1. 环境准备

推荐使用 Conda 创建虚拟环境：

```bash
conda create -n nhg-vrp python=3.9
conda activate nhg-vrp
pip install -r requirements.txt

```

### 2. 数据准备

请确保将竞赛提供的 Excel 数据导出为 CSV，并重命名放入 `data/` 目录：

* `data/orders.csv`
* `data/locations.csv`
* `data/distances.csv`

### 3. 运行探索性分析 (EDA)

启动 Jupyter Notebook 查看数据洞察、瓶颈分析及可视化地图：

```bash
jupyter notebook notebooks/01_exploratory_analysis.ipynb

```

### 4. 运行数据加载测试

验证数据管道是否通畅：

```bash
python src/data_loader.py

```

## 📊 当前进展 (Current Status)

* [x] **数据管道**: 完成 `data_loader.py`，支持动态路径与自动清洗。
* [x] **约束逻辑**: 完成 `utils.py`，已实现 11/14 小时法规校验与 Sleeper Cab 判断逻辑。
* [x] **数据洞察**: 完成 `01_exploratory_analysis.ipynb`，识别出周三/周四为运力瓶颈，并锁定了 Top 10 高货量门店。
* [ ] **核心算法**: 正在开发基于 **Clarke-Wright Savings Algorithm** 的启发式路径构建器。
* [ ] **结果生成**: 待计算年度总里程估算。

## 🛠️ 技术栈 (Tech Stack)

* **Language**: Python 3.9+
* **Data Processing**: Pandas, NumPy
* **Visualization**: Matplotlib, Seaborn
* **IDE**: VS Code / Jupyter

## 📚 参考资料 (References)

1. **Case Study**: Milburn, A. B., Kirac, E., & Hadianniasar, M. (2017). *Growing Pains: A Case Study for Large-Scale Vehicle Routing*. INFORMS Transactions on Education.
2. **Competition**: 2026 IISE Logistics and Supply Chain (LSC) Division Student Case Competition.

---

*Last Updated: February 2026*