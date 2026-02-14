import numpy as np

# --- 核心常量定义 (根据案例要求) ---
SPEED_MPH = 40.0  # 平均车速 40 英里/小时 [cite: 187]
UNLOAD_RATE = 0.030  # 卸货速率 0.030 分钟/立方英尺 [cite: 189]
MIN_UNLOAD_TIME = 30.0  # 最小卸货时间 30 分钟
MAX_DRIVE_HOURS = 11.0  # 单班最大驾驶时间 [cite: 131]
MAX_DUTY_HOURS = 14.0  # 单班最大值勤时间 [cite: 131]
MANDATORY_BREAK = 10.0  # 强制休息时间 10 小时 [cite: 132]
MAX_CAPACITY = 3200  # 拖车最大容积 [cite: 191]


def get_distance(dist_matrix, u, v):
    """
    安全获取两点间距离
    :param dist_matrix: 距离矩阵 DataFrame
    :param u: 起点 Zip
    :param v: 终点 Zip
    """
    try:
        return dist_matrix.loc[u, v]
    except KeyError:
        # 如果找不到距离，返回一个无穷大，避免程序崩溃
        return float('inf')


def calculate_unload_time(volume):
    """
    计算卸货时间 (分钟)
    规则: max(30, 0.030 * volume)
    """
    if volume <= 0: return 0
    calculated = volume * UNLOAD_RATE
    return max(MIN_UNLOAD_TIME, calculated)


def evaluate_route(route, dist_matrix, orders_dict):
    """
    核心评估函数：计算一条路径的里程、时间及是否合规
    :param route: 节点列表，例如 [0, 255, 209, 0] (0代表DC)
    :param dist_matrix: 距离矩阵
    :param orders_dict: 订单字典 {zip_code: volume}
    :return: 包含各项指标的字典
    """
    total_dist = 0.0
    drive_time = 0.0
    duty_time = 0.0  # 值勤时间 = 驾驶 + 卸货 + 等待
    total_volume = 0.0

    # 遍历路径中的每一段
    for i in range(len(route) - 1):
        u = route[i]
        v = route[i + 1]

        # 1. 累加距离
        d = get_distance(dist_matrix, u, str(v))  # 确保索引格式匹配
        # 如果矩阵索引是整数，这里就不用 str(v)
        if isinstance(dist_matrix.index[0], (int, float, np.number)):
            d = get_distance(dist_matrix, u, v)

        total_dist += d

        # 2. 累加时间 (小时)
        segment_drive = d / SPEED_MPH
        drive_time += segment_drive
        duty_time += segment_drive

        # 3. 处理卸货 (到达点 v)
        # 注意: 回到 DC (Node 0) 不需要卸货 [cite: 189]
        if v != 0:
            vol = orders_dict.get(v, 0)
            total_volume += vol

            # 计算卸货耗时 (转为小时)
            unload_min = calculate_unload_time(vol)
            duty_time += (unload_min / 60.0)

    # --- 法规校验 (11/14 小时规则) ---
    is_sleeper = False

    # 逻辑：如果由于路程太远导致违反任何一项时间限制
    # 必须在途中休息 10 小时，但这通常意味着需要过夜车(Sleeper Cab)
    # 在计算总耗时时，是否加上这10小时取决于你的目标函数
    # 题目主要求"Miles"，但必须标记是否可行
    if drive_time > MAX_DRIVE_HOURS or duty_time > MAX_DUTY_HOURS:
        is_sleeper = True
        duty_time += MANDATORY_BREAK  # 加上休息时间 [cite: 132]

    return {
        "total_miles": round(total_dist, 2),
        "drive_hours": round(drive_time, 2),
        "duty_hours": round(duty_time, 2),
        "total_volume": total_volume,
        "is_feasible_capacity": total_volume <= MAX_CAPACITY,
        "needs_sleeper": is_sleeper
    }