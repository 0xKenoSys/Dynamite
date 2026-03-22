import numpy as np
import matplotlib.pyplot as plt
import thermo_core

# 1.1火山参数
GRID_SIZE = 100
OCEAN_DEPTH = -4000.0
MAGMA_TEMP = 1200.0
WATER_TEMP = 2.0
TIME_STEPS = 10000
INJECTION_RATE = 15.0
SHALLOW_WATER_LIMIT = -200.0
SEA_LEVEL = 0.0

# 1.2热力学参数
ALPHA = 1.0e-6  # 岩浆的热扩散率
DT = 1.0    # 时间步长（秒）
DX = 10.0   # 空间网格尺寸（米）
SOLIDIFY_TEMP = 800.0   # 岩浆失去流动性的临界相变温度

# 2. 内存空间分配：高度场与温度场
elevation = np.full((GRID_SIZE, GRID_SIZE), OCEAN_DEPTH, order = 'F')
temperature = np.full((GRID_SIZE,GRID_SIZE), WATER_TEMP, order = 'F')
center_x, center_y = GRID_SIZE // 2, GRID_SIZE // 2
print("系统初始化完成，岩浆开始喷发...")

# 3.物理演化循环（仅保留时间维度）
for t in range(TIME_STEPS):
    # 获取火山口当前最高点
    current_peak = elevation[center_x, center_y]
    # 基础喷发与热量注入
    elevation[center_x, center_y] += INJECTION_RATE
    temperature[center_x, center_y] = MAGMA_TEMP

    # 跨语言调用：将温度场数据抛给Fortran进行极速热传导计算
    # f2py会自动处理 Fortran 返回的 new_temp_grid
    # temperature = thermo_core.thermo_module.solve_heat_conduction(temperature, GRID_SIZE, GRID_SIZE, ALPHA, DT, DX)
    # f2py会自动提取参数，跨语言调用去掉nx,ny
    temperature = thermo_core.thermo_module.solve_heat_conduction(temperature, ALPHA, DT, DX)
    # 获取视图
    center_view = elevation[1:-1, 1:-1]
    temp_view = temperature[1:-1, 1:-1] #获取当前内部网格的温度视图

    north_view = elevation[:-2, 1:-1]
    south_view = elevation[2:, 1:-1]
    west_view = elevation[1:-1, :-2]
    east_view = elevation[1:-1, 2:]

    neighbors_avg = (north_view + south_view + west_view + east_view)/4.0
    # 物理法则分发：根据高度触发不同阶段的逻辑
    if current_peak < SHALLOW_WATER_LIMIT:


        mask_above_ocean = center_view > OCEAN_DEPTH
        mask_steep_drop = (center_view - neighbors_avg) > 20.0

        #新增物理限制：只有温度高于临界临界值的网格才能流动
        mask_fluid_state = temp_view > SOLIDIFY_TEMP

        #高度、深度与温度同时满足条件，岩浆才会发生位移
        active_mask = mask_above_ocean & mask_steep_drop & mask_fluid_state

        flow_amount = (center_view - neighbors_avg) * 0.1 * active_mask

        delta_elevation = np.zeros_like(elevation)

        delta_elevation[1:-1, 1:-1] -= flow_amount * 4

        delta_elevation[:-2, 1:-1] += flow_amount
        delta_elevation[2:, 1:-1] += flow_amount
        delta_elevation[1:-1, :-2] += flow_amount
        delta_elevation[1:-1, 2:] += flow_amount

        elevation += delta_elevation
        # 增加热平流补丁
        temperature[:-2, 1:-1][flow_amount > 0] = MAGMA_TEMP
        temperature[2:, 1:-1][flow_amount > 0] = MAGMA_TEMP
        temperature[1:-1, :-2][flow_amount > 0] = MAGMA_TEMP
        temperature[1:-1, 2:][flow_amount > 0] = MAGMA_TEMP

        # print("阶段一喷发模拟结束，准备渲染...")
        # 要取消缩进，和for循环平级
        print("阶段一喷发模拟结束，准备渲染...")

    elif SHALLOW_WATER_LIMIT <= current_peak < sea_level:
        # 阶段二：蒸汽爆炸、火山口炸碎
        # 1.岩浆流动不规则
        mask_fluid_state = temp_view > SOLIDIFY_TEMP
        flow_amount = (center_view - neighbors_avg) * 0.15 * mask_fluid_state
        # 2.蒸汽爆炸。生成随机掩码
        explosion_probability = 0.05
        explosion_mask = (np.random.ran(GRID_SIZE - 2, GRID_SIZE - 2) < explosion_probability)

        # 高于临界深度才会爆炸
        valid_explosion_zone = (center_view > SHALLOW_WATER_LIMIT) & explosion_mask

        # 爆炸导致高度随机锐减
        blast_damage = np.random.uniform(5.0, 30.0, size=center_view.shape) * valid_explosion_zone

        delta_elevation = np.zeros_like(elevation)
        delta_elevation[1:-1, 1:-1] -= (flow_amount * 4 + blast_damage)

        # 炸碎的岩石随机散落
        delta_elevation[:-2, 1:-1] -= flow_amount + (blast_damage * 0.25)
        delta_elevation[2:, 1:-1] += flow_amount +(blast_damage * 0.25)
        delta_elevation[1:-1, :-2] += flow_amount + (blast_damage * 0.25)
        delta_elevation[1:-1, 2:] += flow_amount + (blast_damage * 0.25)

        elevation += delta_elevation

        # 温度平流
        temperature[:-2, 1:-1][flow_amount > 0] = MAGMA_TEMP
        temperature[2:, 1:-1][flow_amount > 0] = MAGMA_TWMP
        temperature[1:-1, :-2][flow_amount > 0] = MAGMA_TEMP
        temperature[1:-1, 2:][flow_amount > 0] = MAGMA_TEMP

    else:
        # 阶段三：盾状造岛时期
        print("二阶段喷发模拟结束，准备渲染...")

# 4.终端渲染：深海探测器视觉
plt.figure(figsize=(10, 8))

# 下一阶段是什么？工程的目的是最优解、在纵深链路上走到头，走到高并发，而不是一天写二十个玩具项目
# 确定Computer Systems的speciation
# 我需要写一个弹窗，交互程序，问我此时心理淤积额能量是什么，如何解决，如何向内用逻辑理清，如何向外疏导能量。
# 做点题
# 一个小时能抄一节

#使用代表深海和岩石的色彩映射(colormap)
plt.imshow(elevation, cmap='ocean', interpolation='bilinear')
plt.colorbar(label='Elevation(Meters relative to Sea Level)')
plt.title('Kama‘ehuakanaloa (Lo‘ihi) Seamount - Deep Sea Phase')
plt.contour(elevation, levels=20, colors='black', alpha=0.4) #添加等高线增强真实感
plt.show()