import pandas as pd
import numpy as np
from src.utils import evaluate_route, get_distance


class ClarkeWrightSolver:
    def __init__(self, df_orders, df_dist):
        """
        初始化求解器
        :param df_orders: 单日的订单数据 (必须包含 TOZIP, CUBE)
        :param df_dist: 距离矩阵
        """
        self.orders = df_orders.set_index('TOZIP')['CUBE'].to_dict()
        self.dist_matrix = df_dist
        self.routes = []  # 存储路径列表，每条路径是 [0, zip1, zip2, ..., 0]

    def init_routes(self):
        """
        第一步：初始化。假设每个客户都有一辆专车 (DC -> Customer -> DC)
        """
        self.routes = []
        for zip_code in self.orders.keys():
            # 路径格式: [0 (DC), 客户Zip, 0 (DC)]
            route = [0, zip_code, 0]
            self.routes.append(route)

    def calculate_savings(self):
        """
        第二步：计算节约值 S_ij = D_0i + D_0j - D_ij
        返回按节约值降序排列的元组列表: [(savings, i, j), ...]
        """
        savings = []
        customers = list(self.orders.keys())
        n = len(customers)

        for i in range(n):
            for j in range(i + 1, n):
                u = customers[i]
                v = customers[j]

                d_0u = get_distance(self.dist_matrix, 0, u)
                d_0v = get_distance(self.dist_matrix, 0, v)
                d_uv = get_distance(self.dist_matrix, u, v)

                # S_ij = d(0,i) + d(0,j) - d(i,j)
                s = d_0u + d_0v - d_uv
                savings.append((s, u, v))

        # 按节约值从大到小排序
        savings.sort(key=lambda x: x[0], reverse=True)
        return savings

    def find_route_index(self, node):
        """辅助函数：查找某个节点当前在哪条路径中"""
        for idx, route in enumerate(self.routes):
            # 排除掉头尾的 0 (DC)
            if node in route[1:-1]:
                return idx
        return -1

    def solve(self):
        """
        核心执行函数
        """
        # 1. 初始化每人一条路
        self.init_routes()

        # 2. 计算所有可能的合并节约值
        savings_list = self.calculate_savings()

        print(f"开始优化: 初始路径数 {len(self.routes)}, 潜在合并对 {len(savings_list)} 个")

        # 3. 遍历节约值，尝试合并
        for s, i, j in savings_list:
            route_i_idx = self.find_route_index(i)
            route_j_idx = self.find_route_index(j)

            # 如果已经在同一条路，跳过 (避免环路)
            if route_i_idx == route_j_idx:
                continue

            route_i = self.routes[route_i_idx]
            route_j = self.routes[route_j_idx]

            # 判断合并方向 (Clarke-Wright 标准逻辑)
            # 我们只能合并“边缘”节点 (即与 DC 直接相连的节点)
            # Case 1: i 是 Route A 的最后一个点, j 是 Route B 的第一个点 -> Merge A + B
            i_is_last = (route_i[-2] == i)
            j_is_first = (route_j[1] == j)

            # Case 2: i 是 Route A 的第一个点, j 是 Route B 的最后一个点 -> Merge B + A
            i_is_first = (route_i[1] == i)
            j_is_last = (route_j[-2] == j)

            # 尝试构造新路径
            new_route = None
            if i_is_last and j_is_first:
                # 合并: Route I (去掉末尾0) + Route J (去掉开头0)
                new_route = route_i[:-1] + route_j[1:]
            elif i_is_first and j_is_last:
                # 合并: Route J (去掉末尾0) + Route I (去掉开头0)
                new_route = route_j[:-1] + route_i[1:]

            # 如果符合合并条件，检查约束 (容量 & 时间)
            if new_route:
                metrics = evaluate_route(new_route, self.dist_matrix, self.orders)

                # 核心约束检查:
                # 1. 容量必须满足 (<= 3200)
                # 2. 时间窗必须满足 (这里简化为 evaluate_route 返回的可行性)
                # 注意: 即使需要 Sleeper Cab (metrics['needs_sleeper'] == True) 也是允许的，只要不超过 14+10 小时

                if metrics['is_feasible_capacity']:
                    # 这里还可以加一个判断: if metrics['duty_hours'] < 24 (硬性极限)

                    # 执行合并: 更新 routes 列表
                    # 移除旧的两条，加入新的一条
                    # 技巧: 先移除 index 大的，再移除小的，防止索引移位
                    idx_list = sorted([route_i_idx, route_j_idx], reverse=True)
                    for idx in idx_list:
                        self.routes.pop(idx)

                    self.routes.append(new_route)

        return self.routes