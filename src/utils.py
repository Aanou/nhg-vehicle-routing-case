import numpy as np

# --- 核心常量定义 ---
SPEED_MPH = 40.0  # 平均车速
UNLOAD_RATE = 0.030  # 卸货速率
MIN_UNLOAD_TIME = 30.0  # 最小卸货时间
MAX_DRIVE_HOURS = 11.0  # 11小时驾驶限制
MAX_DUTY_HOURS = 14.0  # 14小时值勤限制
MANDATORY_BREAK = 10.0  # 强制休息
MAX_CAPACITY = 3200  # 拖车容量
DEPOT_ZIP = 1887  # <--- 新增: 定义配送中心的真实邮编


def get_distance(dist_matrix, u, v):
    """
    安全获取两点间距离，自动处理 Depot ID (0 -> 1887)
    """
    # 1. 如果节点是 0 (ORDERID)，转换为真实的 Zip Code
    real_u = DEPOT_ZIP if u == 0 else u
    real_v = DEPOT_ZIP if v == 0 else v

    # 2. 查表
    try:
        # 尝试直接获取
        return dist_matrix.loc[real_u, real_v]
    except KeyError:
        # 3. 容错处理: 可能是数据类型不匹配 (比如一个是 int 1887, 一个是 str "1887")
        try:
            return dist_matrix.loc[int(real_u), int(real_v)]
        except KeyError:
            # 如果真的找不到，打印警告并返回无穷大
            # print(f"⚠️ 警告: 距离矩阵中找不到 {real_u} -> {real_v}")
            return float('inf')


def calculate_unload_time(volume):
    """计算卸货时间 (分钟)"""
    if volume <= 0: return 0
    calculated = volume * UNLOAD_RATE
    return max(MIN_UNLOAD_TIME, calculated)


def evaluate_route(route, dist_matrix, orders_dict):
    """
    核心评估函数
    """
    total_dist = 0.0
    drive_time = 0.0
    duty_time = 0.0
    total_volume = 0.0

    # 遍历路径
    for i in range(len(route) - 1):
        u = route[i]
        v = route[i + 1]

        # 获取距离 (会自动处理 0 -> 1887)
        d = get_distance(dist_matrix, u, v)

        # 如果距离是无穷大，说明数据有问题，直接中断
        if d == float('inf'):
            print(f"❌ 严重错误: 无法计算距离 {u} -> {v}")
            return {
                "total_miles": float('inf'), "drive_hours": float('inf'),
                "duty_hours": float('inf'), "total_volume": float('inf'),
                "is_feasible_capacity": False, "needs_sleeper": False
            }

        total_dist += d

        # 累加时间
        segment_drive = d / SPEED_MPH
        drive_time += segment_drive
        duty_time += segment_drive

        # 累加卸货 (排除回程 DC)
        if v != 0:
            vol = orders_dict.get(v, 0)
            total_volume += vol
            unload_min = calculate_unload_time(vol)
            duty_time += (unload_min / 60.0)

    # 法规校验
    is_sleeper = False
    if drive_time > MAX_DRIVE_HOURS or duty_time > MAX_DUTY_HOURS:
        is_sleeper = True
        duty_time += MANDATORY_BREAK

    return {
        "total_miles": round(total_dist, 2),
        "drive_hours": round(drive_time, 2),
        "duty_hours": round(duty_time, 2),
        "total_volume": total_volume,
        "is_feasible_capacity": total_volume <= MAX_CAPACITY,
        "needs_sleeper": is_sleeper
    }