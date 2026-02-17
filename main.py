import pandas as pd
import os
import sys

# 动态添加项目根目录到路径，确保能导入 src 下的模块
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from src.data_loader import load_data
from src.model import ClarkeWrightSolver
from src.utils import evaluate_route


def run_weekly_simulation():
    print("🚀 启动 NHG 物流路径优化求解器...")

    # 1. 加载数据
    # 注意: load_data 现在返回三个 DataFrame
    df_orders, df_locs, df_dist = load_data()

    # 2. 按星期分组 (Monday - Friday)
    # 案例要求: 不同日期的订单不能混装 [cite: 195]
    days_of_week = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']

    weekly_routes = []
    total_weekly_miles = 0.0

    print(f"\n{'=' * 50}")
    print(f"{'DAY':<10} | {'ROUTES':<8} | {'MILES':<10} | {'SLEEPERS':<8}")
    print(f"{'-' * 50}")

    for day in days_of_week:
        # 筛选当天的订单
        day_orders = df_orders[df_orders['DayOfWeek'] == day].copy()

        if day_orders.empty:
            print(f"{day:<10} | 0        | 0.00       | 0")
            continue

        # 3. 实例化求解器并运行
        # 传入当天的订单和全局距离矩阵
        solver = ClarkeWrightSolver(day_orders, df_dist)
        daily_routes = solver.solve()

        # 4. 评估当天的结果
        day_miles = 0.0
        sleeper_count = 0

        # 为了评估，我们需要一个 {zip: volume} 的字典
        orders_dict = day_orders.set_index('TOZIP')['CUBE'].to_dict()

        for route in daily_routes:
            # 评估单条路径 (计算里程、时间、是否需要过夜)
            metrics = evaluate_route(route, df_dist, orders_dict)

            day_miles += metrics['total_miles']
            if metrics['needs_sleeper']:
                sleeper_count += 1

            # 记录详细结果以便导出 CSV
            weekly_routes.append({
                'Day': day,
                'Route_ID': f"{day}_{len(weekly_routes) + 1}",
                'Stops': str(route),  # 将列表转为字符串保存
                'Num_Stops': len(route) - 2,  # 减去头尾的 DC
                'Total_Miles': metrics['total_miles'],
                'Drive_Hours': metrics['drive_hours'],
                'Duty_Hours': metrics['duty_hours'],
                'Total_Volume': metrics['total_volume'],
                'Capacity_Util': round(metrics['total_volume'] / 3200 * 100, 1),
                'Needs_Sleeper': 'Yes' if metrics['needs_sleeper'] else 'No'
            })

        total_weekly_miles += day_miles

        # 打印每日摘要
        print(f"{day:<10} | {len(daily_routes):<8} | {day_miles:,.2f}   | {sleeper_count}")

    print(f"{'=' * 50}")

    # 5. 计算年度总里程 (乘以 52 周) [cite: 92, 125]
    annual_miles = total_weekly_miles * 52

    print(f"\n📊 最终结果摘要:")
    print(f"   周总里程: {total_weekly_miles:,.2f} miles")
    print(f"   年度估算: {annual_miles:,.2f} miles")

    # 6. 保存详细结果
    project_root = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(project_root, 'results')

    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
        print(f"📁 已自动创建文件夹: {results_dir}")

    output_csv = os.path.join(results_dir, 'final_schedule.csv')
    pd.DataFrame(weekly_routes).to_csv(output_csv, index=False)

    print(f"\n💾 详细排程表已保存至: {output_csv}")


if __name__ == "__main__":
    run_weekly_simulation()