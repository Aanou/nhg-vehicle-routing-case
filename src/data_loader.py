import pandas as pd
from pathlib import Path
import sys
import numpy as np


def load_data():
    # 1. 自动定位 data 目录
    data_dir = Path(__file__).parent.parent / 'data'

    print(f"正在从 {data_dir} 读取数据...")

    # 2. 读取文件
    try:
        df_orders = pd.read_csv(data_dir / 'orders.csv')
        df_locs = pd.read_csv(data_dir / 'locations.csv')
        # index_col=0: 把第一列当作索引
        df_dist = pd.read_csv(data_dir / 'distances.csv', index_col=0)
    except FileNotFoundError as e:
        print(f"❌ 文件未找到: {e}")
        sys.exit(1)

    # 3. 清洗列名 (去空格)
    df_orders.columns = df_orders.columns.str.strip()
    df_locs.columns = df_locs.columns.str.strip()

    # --- 关键修复开始: 清理距离矩阵 ---

    # A. 剔除脏数据: 如果索引中有 'Zip' 这个单词，删掉这一行
    if 'Zip' in df_dist.index:
        df_dist = df_dist.drop('Zip')

    # B. 剔除脏列: 如果列名中有 'Zip'，也删掉
    if 'Zip' in df_dist.columns:
        df_dist = df_dist.drop(columns=['Zip'])

    # C. 强制转换索引为整数 (Int)
    # 使用 pd.to_numeric 强制转，无法转的变成 NaN，然后删掉
    df_dist.index = pd.to_numeric(df_dist.index, errors='coerce')
    df_dist = df_dist[df_dist.index.notna()]  # 删掉转换失败的行
    df_dist.index = df_dist.index.astype(int)  # 转为纯整数

    # D. 强制转换列名为整数 (Int)
    df_dist.columns = pd.to_numeric(df_dist.columns, errors='coerce')
    # 如果列转换失败变成了 NaN，我们只保留有效的数字列
    valid_cols = df_dist.columns.notna()
    df_dist = df_dist.loc[:, valid_cols]
    df_dist.columns = df_dist.columns.astype(int)

    # --- 关键修复结束 ---

    # 4. 常规清洗订单表
    # 兼容 ORDERID 可能的大小写问题
    id_col = next((c for c in df_orders.columns if 'ORDER' in c.upper()), None)
    if id_col:
        # 过滤掉 DC (ORDERID=0)
        df_orders = df_orders[df_orders[id_col] != 0].copy()

    # 确保数值格式
    df_orders['CUBE'] = pd.to_numeric(df_orders['CUBE'], errors='coerce')
    df_orders['TOZIP'] = pd.to_numeric(df_orders['TOZIP'], errors='coerce')

    print(f"✅ 成功加载: {len(df_orders)} 个订单")
    print(f"📊 距离矩阵维度: {df_dist.shape}")
    # 验证一下 1887 是否存在
    if 1887 in df_dist.index:
        print("✅ 验证通过: 距离矩阵包含 Depot (1887)")
    else:
        print("⚠️ 警告: 距离矩阵中未找到 Depot (1887)，请检查是否为 0")

    return df_orders, df_locs, df_dist


if __name__ == "__main__":
    orders, locs, dists = load_data()