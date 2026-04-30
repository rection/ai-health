<template>
  <div>
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="8">
        <el-card>
          <template #header>今日热量</template>
          <div style="font-size: 28px; font-weight: bold; color: #409EFF">{{ todayCalories }} kcal</div>
          <div style="color: #999; margin-top: 8px">推荐摄入 2000 kcal</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>今日记录</template>
          <div style="font-size: 28px; font-weight: bold; color: #67C23A">{{ todayMeals }} 餐</div>
          <div style="color: #999; margin-top: 8px">早餐/午餐/晚餐/加餐</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>本周运动</template>
          <div style="font-size: 28px; font-weight: bold; color: #E6A23C">{{ weekExercise }} 次</div>
          <div style="color: #999; margin-top: 8px">坚持运动，健康生活</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="16">
        <el-card>
          <template #header>本周营养趋势</template>
          <div ref="chartRef" style="height: 300px"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>AI 今日建议</template>
          <div v-if="aiTip" style="white-space: pre-line; line-height: 1.8">{{ aiTip }}</div>
          <el-button v-else type="primary" @click="getAITip">获取 AI 建议</el-button>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import request from '../../api/request'
import dayjs from 'dayjs'

const todayCalories = ref(0)
const todayMeals = ref(0)
const weekExercise = ref(0)
const aiTip = ref('')
const chartRef = ref<HTMLElement>()
let chart: echarts.ECharts | null = null

async function loadDashboard() {
  const today = dayjs().format('YYYY-MM-DD')
  const weekAgo = dayjs().subtract(7, 'day').format('YYYY-MM-DD')

  try {
    const logs: any = await request.get('/daily-logs', { params: { start_date: today, end_date: today } })
    todayMeals.value = logs.length
    todayCalories.value = logs.reduce((sum: number, log: any) => sum + (log.total_calories || 0), 0)

    const exercises: any = await request.get('/exercise-logs', { params: { start_date: weekAgo, end_date: today } })
    weekExercise.value = exercises.length

    const trend: any = await request.get('/analytics/nutrition-trend', { params: { days: 7 } })
    renderChart(trend)
  } catch {}
}

function renderChart(data: any[]) {
  if (!chartRef.value) return
  chart = echarts.init(chartRef.value)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['热量(kcal)', '蛋白质(g)', '脂肪(g)', '碳水(g)'] },
    xAxis: { type: 'category', data: data.map(d => d.date) },
    yAxis: { type: 'value' },
    series: [
      { name: '热量(kcal)', type: 'line', data: data.map(d => d.calories) },
      { name: '蛋白质(g)', type: 'line', data: data.map(d => d.protein) },
      { name: '脂肪(g)', type: 'line', data: data.map(d => d.fat) },
      { name: '碳水(g)', type: 'line', data: data.map(d => d.carbs) },
    ],
  })
}

async function getAITip() {
  try {
    const res: any = await request.post('/recommendations/diet')
    aiTip.value = JSON.stringify(res.content, null, 2)
  } catch {}
}

onMounted(() => {
  loadDashboard()
  window.addEventListener('resize', () => chart?.resize())
})

onUnmounted(() => {
  chart?.dispose()
})
</script>
