<template>
  <div>
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>营养摄入趋势</template>
          <div ref="nutritionChartRef" style="height: 350px"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>热量收支平衡</template>
          <div ref="calorieChartRef" style="height: 350px"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-card>
      <template #header>体重变化</template>
      <div style="text-align: center; padding: 40px; color: #999">
        当前体重：{{ currentWeight || '未设置' }} kg
        <div style="margin-top: 8px; font-size: 13px">定期更新体重以追踪变化趋势</div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import request from '../../api/request'

const nutritionChartRef = ref<HTMLElement>()
const calorieChartRef = ref<HTMLElement>()
const currentWeight = ref<number | null>(null)
let nutritionChart: echarts.ECharts | null = null
let calorieChart: echarts.ECharts | null = null

async function loadData() {
  try {
    const trend: any = await request.get('/analytics/nutrition-trend', { params: { days: 30 } })
    renderNutritionChart(trend)
    renderCalorieChart(trend)

    const weight: any = await request.get('/analytics/weight-trend')
    currentWeight.value = weight.current_weight
  } catch {}
}

function renderNutritionChart(data: any[]) {
  if (!nutritionChartRef.value) return
  nutritionChart = echarts.init(nutritionChartRef.value)
  nutritionChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['蛋白质(g)', '脂肪(g)', '碳水(g)'] },
    xAxis: { type: 'category', data: data.map(d => d.date.slice(5)) },
    yAxis: { type: 'value', name: '克(g)' },
    series: [
      { name: '蛋白质(g)', type: 'bar', stack: 'nutrient', data: data.map(d => d.protein) },
      { name: '脂肪(g)', type: 'bar', stack: 'nutrient', data: data.map(d => d.fat) },
      { name: '碳水(g)', type: 'bar', stack: 'nutrient', data: data.map(d => d.carbs) },
    ],
  })
}

function renderCalorieChart(data: any[]) {
  if (!calorieChartRef.value) return
  calorieChart = echarts.init(calorieChartRef.value)
  calorieChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: data.map(d => d.date.slice(5)) },
    yAxis: { type: 'value', name: 'kcal' },
    series: [
      {
        name: '每日热量',
        type: 'line',
        data: data.map(d => d.calories),
        markLine: { data: [{ yAxis: 2000, label: { formatter: '推荐2000kcal' } }] },
      },
    ],
  })
}

onMounted(() => {
  loadData()
  window.addEventListener('resize', () => {
    nutritionChart?.resize()
    calorieChart?.resize()
  })
})

onUnmounted(() => {
  nutritionChart?.dispose()
  calorieChart?.dispose()
})
</script>
