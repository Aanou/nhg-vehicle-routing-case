import os
import sys
import pandas as pd
import os

from src.data_loader import load_data
from src.model import ClarkeWrightSolver
from src.utils import evaluate_route

# 动态添加项目根目录到路径，确保能导入 src 下的模块
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)


def run_simulation():
    print("🚀 启动 NHG 物流路径优化系统...")

    # 1. 加载数据
    try:
        df_orders, df_locs, df_dist = load_data()
    except Exception as e:
        print(f"❌ 数据加载失败: {e}")
        return

    # 2. 准备循环
    days_of_week = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
    weekly_routes = []

    # 用于控制台打印的累加器
    total_weekly_miles = 0.0
    total_weekly_duty = 0.0
    total_sleepers = 0

    print(f"\n{'=' * 65}")
    print(f"{'DAY':<5} | {'ROUTES':<6} | {'MILES':<10} | {'HOURS (Duty)':<12} | {'SLEEPERS':<8}")
    print(f"{'-' * 65}")

    for day in days_of_week:
        day_orders = df_orders[df_orders['DayOfWeek'] == day].copy()

        if day_orders.empty:
            continue

        # 3. 求解
        solver = ClarkeWrightSolver(day_orders, df_dist)
        daily_routes = solver.solve()

        # 4. 统计
        day_miles = 0.0
        day_duty = 0.0
        day_sleepers = 0

        day_orders_dict = day_orders.set_index('TOZIP')['CUBE'].to_dict()

        for route in daily_routes:
            metrics = evaluate_route(route, df_dist, day_orders_dict)

            day_miles += metrics['total_miles']
            day_duty += metrics['duty_hours']
            if metrics['needs_sleeper']:
                day_sleepers += 1

            # 添加明细行
            weekly_routes.append({
                'Type': 'Route Detail',  # 标记这一行是明细
                'Day': day,
                'Route_Structure': str(route),
                'Stops_Count': len(route) - 2,
                'Total_Miles': metrics['total_miles'],
                'Duty_Hours': metrics['duty_hours'],
                'Capacity_Util': f"{metrics['total_volume'] / 3200:.1%}",
                'Sleeper_Required': 'Yes' if metrics['needs_sleeper'] else 'No'
            })

        total_weekly_miles += day_miles
        total_weekly_duty += day_duty
        total_sleepers += day_sleepers

        print(f"{day:<5} | {len(daily_routes):<6} | {day_miles:,.2f}   | {day_duty:,.2f}        | {day_sleepers}")

    print(f"{'=' * 65}")

    # 5. 计算年度汇总
    annual_miles = total_weekly_miles * 52
    annual_duty = total_weekly_duty * 52
    annual_sleepers = total_sleepers * 52

    print(f"\n🏆 最终结果:")
    print(f"   周总里程: {total_weekly_miles:,.2f} miles")
    print(f"   年度估算: {annual_miles:,.2f} miles")

    # --- 新增: 添加汇总行到 CSV ---

    # 添加一个空行作为分隔 (在Excel里看起来更清楚)
    weekly_routes.append({})

    # 添加周汇总行
    weekly_routes.append({
        'Type': 'WEEKLY TOTAL',
        'Day': 'ALL',
        'Total_Miles': round(total_weekly_miles, 2),
        'Duty_Hours': round(total_weekly_duty, 2),
        'Sleeper_Required': total_sleepers
    })

    # 添加年汇总行
    weekly_routes.append({
        'Type': 'ANNUAL ESTIMATE',
        'Day': '52 Weeks',
        'Total_Miles': round(annual_miles, 2),
        'Duty_Hours': round(annual_duty, 2),
        'Sleeper_Required': annual_sleepers
    })

    # ---------------------------

    # 6. 保存
    project_root = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(project_root, 'results')

    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    output_csv = os.path.join(results_dir, 'final_schedule.csv')

    # 保存时，确保 Total_Miles 列在前面，方便查看
    df_out = pd.DataFrame(weekly_routes)
    # 调整列顺序 (可选)
    cols = ['Type', 'Day', 'Total_Miles', 'Duty_Hours', 'Sleeper_Required', 'Route_Structure', 'Stops_Count',
            'Capacity_Util']
    # 仅选择存在的列防止报错
    cols = [c for c in cols if c in df_out.columns]
    df_out = df_out[cols]

    df_out.to_csv(output_csv, index=False)
    print(f"\n💾 包含汇总数据的排程表已保存至: {output_csv}")


if __name__ == "__main__":
    run_simulation()
