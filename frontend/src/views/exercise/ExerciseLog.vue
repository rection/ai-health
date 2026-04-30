<template>
  <div>
    <el-card style="margin-bottom: 20px">
      <template #header>添加运动记录</template>
      <el-form :model="form" inline>
        <el-form-item label="日期">
          <el-date-picker v-model="form.date" type="date" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="运动类型">
          <el-select v-model="form.exercise_type" filterable allow-create>
            <el-option label="跑步" value="跑步" />
            <el-option label="快走" value="快走" />
            <el-option label="游泳" value="游泳" />
            <el-option label="骑车" value="骑车" />
            <el-option label="瑜伽" value="瑜伽" />
            <el-option label="力量训练" value="力量训练" />
            <el-option label="跳绳" value="跳绳" />
            <el-option label="篮球" value="篮球" />
            <el-option label="羽毛球" value="羽毛球" />
          </el-select>
        </el-form-item>
        <el-form-item label="时长(分钟)">
          <el-input-number v-model="form.duration_min" :min="1" :max="480" />
        </el-form-item>
        <el-form-item label="消耗(kcal)">
          <el-input-number v-model="form.calories_burned" :min="0" :precision="0" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="addExercise">添加</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card>
      <template #header>运动记录</template>
      <el-table :data="exercises" style="width: 100%">
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column prop="exercise_type" label="运动类型" />
        <el-table-column prop="duration_min" label="时长(分钟)" />
        <el-table-column prop="calories_burned" label="消耗(kcal)" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import request from '../../api/request'
import dayjs from 'dayjs'
import { ElMessage } from 'element-plus'

const exercises = ref<any[]>([])
const form = reactive({
  date: dayjs().format('YYYY-MM-DD'),
  exercise_type: '',
  duration_min: 30,
  calories_burned: 0,
})

async function loadExercises() {
  const today = dayjs().format('YYYY-MM-DD')
  const monthAgo = dayjs().subtract(30, 'day').format('YYYY-MM-DD')
  exercises.value = await request.get('/exercise-logs', {
    params: { start_date: monthAgo, end_date: today },
  })
}

async function addExercise() {
  if (!form.exercise_type) {
    ElMessage.warning('请选择运动类型')
    return
  }
  await request.post('/exercise-logs', form)
  ElMessage.success('添加成功')
  form.exercise_type = ''
  form.duration_min = 30
  form.calories_burned = 0
  await loadExercises()
}

onMounted(loadExercises)
</script>
