<template>
  <div>
    <el-card style="margin-bottom: 20px">
      <el-date-picker v-model="selectedDate" type="date" placeholder="选择日期" format="YYYY-MM-DD" value-format="YYYY-MM-DD" @change="loadLogs" />
    </el-card>

    <el-row :gutter="20">
      <el-col :span="6" v-for="meal in meals" :key="meal.type">
        <el-card>
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center">
              <span>{{ meal.label }}</span>
              <el-button type="primary" size="small" @click="openAddDialog(meal.type)">添加</el-button>
            </div>
          </template>
          <div v-if="getLogByMeal(meal.type)?.items?.length">
            <div v-for="item in getLogByMeal(meal.type)!.items" :key="item.id" style="padding: 8px 0; border-bottom: 1px solid #eee; display: flex; justify-content: space-between">
              <div>
                <div>{{ item.food_name || item.custom_name }}</div>
                <div style="color: #999; font-size: 12px">{{ item.quantity_g }}g</div>
              </div>
              <div style="display: flex; align-items: center; gap: 8px">
                <span style="color: #E6A23C">{{ item.calories?.toFixed(0) }} kcal</span>
                <el-button type="danger" size="small" link @click="deleteItem(getLogByMeal(meal.type)!.id, item.id)">删除</el-button>
              </div>
            </div>
            <div style="text-align: right; margin-top: 10px; font-weight: bold">
              合计: {{ getLogByMeal(meal.type)!.total_calories.toFixed(0) }} kcal
            </div>
          </div>
          <el-empty v-else description="暂无记录" :image-size="60" />
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="dialogVisible" title="添加食物" width="500px">
      <el-form :model="addForm">
        <el-form-item label="搜索食物">
          <el-select v-model="addForm.food_id" filterable remote :remote-method="searchFoods" placeholder="输入食物名称搜索" style="width: 100%">
            <el-option v-for="food in foodOptions" :key="food.id" :label="`${food.name} (${food.calories_per_100g}kcal/100g)`" :value="food.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="或自定义食物">
          <el-input v-model="addForm.custom_name" placeholder="输入食物名称" />
        </el-form-item>
        <el-form-item label="食用量(g)">
          <el-input-number v-model="addForm.quantity_g" :min="1" :max="5000" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="addItem">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import request from '../../api/request'
import dayjs from 'dayjs'
import { ElMessage } from 'element-plus'

const selectedDate = ref(dayjs().format('YYYY-MM-DD'))
const logs = ref<any[]>([])
const dialogVisible = ref(false)
const currentMealType = ref('')
const foodOptions = ref<any[]>([])

const meals = [
  { type: 'breakfast', label: '早餐' },
  { type: 'lunch', label: '午餐' },
  { type: 'dinner', label: '晚餐' },
  { type: 'snack', label: '加餐' },
]

const addForm = reactive({
  food_id: null as number | null,
  quantity_g: 100,
  custom_name: '',
})

function getLogByMeal(type: string) {
  return logs.value.find(l => l.meal_type === type)
}

async function loadLogs() {
  logs.value = await request.get('/daily-logs', {
    params: { start_date: selectedDate.value, end_date: selectedDate.value },
  })
}

async function searchFoods(query: string) {
  if (!query) return
  foodOptions.value = await request.get('/foods/search', { params: { q: query } })
}

async function openAddDialog(mealType: string) {
  currentMealType.value = mealType
  addForm.food_id = null
  addForm.quantity_g = 100
  addForm.custom_name = ''
  foodOptions.value = []

  let log = getLogByMeal(mealType)
  if (!log) {
    log = await request.post('/daily-logs', { date: selectedDate.value, meal_type: mealType })
    await loadLogs()
  }
  dialogVisible.value = true
}

async function addItem() {
  const log = getLogByMeal(currentMealType.value)
  if (!log) return
  if (!addForm.food_id && !addForm.custom_name) {
    ElMessage.warning('请选择食物或输入自定义名称')
    return
  }
  await request.post(`/daily-logs/${log.id}/items`, {
    food_id: addForm.food_id,
    quantity_g: addForm.quantity_g,
    custom_name: addForm.custom_name || null,
  })
  dialogVisible.value = false
  ElMessage.success('添加成功')
  await loadLogs()
}

async function deleteItem(logId: number, itemId: number) {
  await request.delete(`/daily-logs/${logId}/items/${itemId}`)
  ElMessage.success('删除成功')
  await loadLogs()
}

onMounted(loadLogs)
</script>
