import numpy as np
import matplotlib.pyplot as plt

# 1.火山参数
GRID_SIZE = 100
OCEAN_DEPTH = -4000.0
MAGMA_TEMP = 1200.0
WATER_TEMP = 2.0
TIME_STEPS = 500
INJECTION_RATE = 15.0

# 2. 内存空间分配：高度场与温度场
elevation = np.full((GRID_SIZE, GRID_SIZE), OCEAN_DEPTH)
temperature = np.full((GRID_SIZE,GRID_SIZE), WATER_TEMP)
center_x, center_y = GRID_SIZE // 2, GRID_SIZE // 2
print("系统初始化完成，岩浆开始喷发...")

# 3.物理演化循环（仅保留时间维度）
for t in range(TIME_STEPS):
    elevation[center_x, center_y] += INJECTION_RATE
    temperature[center_x, center_y] = MAGMA_TEMP
    center_view = elevation[1:-1, 1:-1]

    north_view = elevation[:-2, 1:-1]
    south_view = elevation[2:, 1:-1]
    west_view = elevation[1:-1, :-2]
    east_view = elevation[1:-1, 2:]

    neighbors_avg = (north_view + south_view + west_view + east_view)/4.0

    mask_above_ocean = center_view > OCEAN_DEPTH
    mask_steep_drop = (center_view - neighbors_avg) > 20.0

    actice_mask = mask_above_ocean & mask_steep_drop

    flow_amount = (center_view - neighbors_avg)*0.1*actice_mask

    delta_elevation = np.zeros_like(elevation)

    delta_elevation[1:-1, 1:-1] -= flow_amount * 4

    delta_elevation[:-2, 1:-1] += flow_amount
    delta_elevation[2:, 1:-1] += flow_amount
    delta_elevation[1:-1, :-2] += flow_amount
    delta_elevation[1:-1, 2:] += flow_amount

    elevation += delta_elevation

    print("阶段一喷发模拟结束，准备渲染...")

# 4.终端渲染：深海探测器视觉
plt.figure(figsize=(10, 8))

#使用代表深海和岩石的色彩映射(colormap)
plt.imshow(elevation, cmap='ocean', interpolation='bilinear')
plt.colorbar(label='Elevation(Meters relative to Sea Level)')
plt.title('Kama‘ehuakanaloa (Lo‘ihi) Seamount - Deep Sea Phase')
plt.contour(elevation, levels=20, colors='black', alpha=0.4) #添加等高线增强真实感
plt.show()