import numpy as np
import matplotlib.pyplot as plt

# 1.火山参数
GRID_SIZE = 100
OCEAN_DEPTH = -4000.0
MAGMA_TEMP = 1200.0
WATER_TEMP = 2.0

# 2. 高度场与温度场
elevation = np.full((GRID_SIZE, GRID_SIZE), OCEAN_DEPTH)

temperature = np.full((GRID_SIZE,GRID_SIZE), WATER_TEMP)
center_x, center_y = GRID_SIZE // 2, GRID_SIZE // 2

# 3.物理演化循环
TIME_STEPS = 500
INJECTION_RATE = 15.0
print("海底地壳撕裂，火山开始喷发...")

for t in range(TIME_STEPS):
    elevation[center_x, center_y] += INJECTION_RATE
    temperature[center_x, center_y] = MAGMA_TEMP

    #枕状熔岩
    #Cellular Automata Logic
    for i in range(1, GRID_SIZE - 1):
        for j in range(1, GRID_SIZE - 1):

            #高差检测
            if elevation[i, j] > OCEAN_DEPTH:
                #平均高差
                neighbors_avg = (elevation[i+1, j] + elevation[i-1, j]+ elevation[i, j+1] + elevation[i, j-1])/4
                #如果高差大于20，溢出
                if elevation[i, j] - neighbors_avg > 20.0:
                    flow_amount = (elevation[i, j] - neighbors_avg)*0.1
                    elevation[i, j] -= flow_amount * 4
                    elevation[i+1, j] += flow_amount
                    elevation[i-1, j] += flow_amount
                    elevation[i, j+1] += flow_amount
                    elevation[i, j-1] += flow_amount
                    print("阶段一喷发模拟结束，准备渲染...")

# 4.终端渲染：深海探测器视觉
plt.figure(figsize=(8, 6))

#使用代表深海和岩石的色彩映射(colormap)
plt.imshow(elevation, cmap='ocean', interpolation='bilinear')
plt.colorbar(label='Elevation(Meters relative to Sea Level)')
plt.title('Kama‘ehuakanaloa (Lo‘ihi) Seamount - Deep Sea Phase')
plt.contour(elevation, levels=15, colors='black', alpha=0.3) #添加等高线增强真实感
plt.show()