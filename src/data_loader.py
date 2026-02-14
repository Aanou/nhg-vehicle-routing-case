import pandas as pd
from pathlib import Path


def load_data():
    # 1. 自动定位 data 目录 (当前脚本的上一级目录下的 data 文件夹)
    data_dir = Path(__file__).parent.parent / 'data'

    # 2. 读取文件
    print(f"正在从 {data_dir} 读取数据...")
    df_orders = pd.read_csv(data_dir / 'orders.csv')
    df_locs = pd.read_csv(data_dir / 'locations.csv')
    df_dist = pd.read_csv(data_dir / 'distances.csv', index_col=0)  # 第一列设为索引


    # 3. 简单清洗
    # 过滤掉 DC (ORDERID=0)，只保留客户订单
    df_orders = df_orders[df_orders['ORDERID'] != 0].copy()

    # 确保体积和邮编是数字格式
    df_orders['CUBE'] = pd.to_numeric(df_orders['CUBE'], errors='coerce')
    df_orders['TOZIP'] = pd.to_numeric(df_orders['TOZIP'], errors='coerce')

    print(f"✅ 成功加载: {len(df_orders)} 个订单")
    return df_orders, df_locs, df_dist


if __name__ == "__main__":
    orders, locs, dists = load_data()
    print(orders.head())