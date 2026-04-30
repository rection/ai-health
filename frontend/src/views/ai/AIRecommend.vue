<template>
  <div>
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center">
              <span>饮食推荐</span>
              <el-button type="primary" :loading="dietLoading" @click="getDietRecommend">获取推荐</el-button>
            </div>
          </template>
          <div v-if="dietResult">
            <el-collapse>
              <el-collapse-item title="早餐" name="1">
                <div v-for="item in dietResult.content?.breakfast" :key="item.name" style="padding: 4px 0">
                  {{ item.name }} - {{ item.amount }} ({{ item.calories }} kcal)
                </div>
              </el-collapse-item>
              <el-collapse-item title="午餐" name="2">
                <div v-for="item in dietResult.content?.lunch" :key="item.name" style="padding: 4px 0">
                  {{ item.name }} - {{ item.amount }} ({{ item.calories }} kcal)
                </div>
              </el-collapse-item>
              <el-collapse-item title="晚餐" name="3">
                <div v-for="item in dietResult.content?.dinner" :key="item.name" style="padding: 4px 0">
                  {{ item.name }} - {{ item.amount }} ({{ item.calories }} kcal)
                </div>
              </el-collapse-item>
            </el-collapse>
            <div v-if="dietResult.content?.reason" style="margin-top: 12px; padding: 12px; background: #f5f7fa; border-radius: 4px">
              <strong>建议原因：</strong>{{ dietResult.content.reason }}
            </div>
          </div>
          <el-empty v-else description="点击按钮获取 AI 饮食推荐" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center">
              <span>运动推荐</span>
              <el-button type="primary" :loading="exerciseLoading" @click="getExerciseRecommend">获取推荐</el-button>
            </div>
          </template>
          <div v-if="exerciseResult">
            <div v-for="item in exerciseResult.content?.recommended_exercises" :key="item.name" style="padding: 8px 0; border-bottom: 1px solid #eee">
              <div style="font-weight: bold">{{ item.name }}</div>
              <div style="color: #666; font-size: 13px">{{ item.duration }} | {{ item.intensity }}</div>
              <div style="color: #999; font-size: 12px">{{ item.benefit }}</div>
            </div>
            <div v-if="exerciseResult.content?.precautions?.length" style="margin-top: 12px; padding: 12px; background: #fdf6ec; border-radius: 4px">
              <strong>注意事项：</strong>
              <div v-for="p in exerciseResult.content.precautions" :key="p" style="margin-top: 4px">{{ p }}</div>
            </div>
          </div>
          <el-empty v-else description="点击按钮获取 AI 运动推荐" />
        </el-card>
      </el-col>
    </el-row>

    <el-card>
      <template #header>历史推荐</template>
      <el-table :data="history" style="width: 100%">
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column prop="recommendation_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.recommendation_type === 'diet' ? 'success' : 'warning'">
              {{ row.recommendation_type === 'diet' ? '饮食' : '运动' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="内容">
          <template #default="{ row }">
            <el-button link type="primary" @click="showDetail(row)">查看详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="detailVisible" title="推荐详情" width="600px">
      <pre style="white-space: pre-wrap; font-size: 13px">{{ JSON.stringify(detailContent, null, 2) }}</pre>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import request from '../../api/request'
import { ElMessage } from 'element-plus'

const dietLoading = ref(false)
const exerciseLoading = ref(false)
const dietResult = ref<any>(null)
const exerciseResult = ref<any>(null)
const history = ref<any[]>([])
const detailVisible = ref(false)
const detailContent = ref<any>(null)

async function getDietRecommend() {
  dietLoading.value = true
  try {
    dietResult.value = await request.post('/recommendations/diet')
    ElMessage.success('饮食推荐生成成功')
    await loadHistory()
  } finally {
    dietLoading.value = false
  }
}

async function getExerciseRecommend() {
  exerciseLoading.value = true
  try {
    exerciseResult.value = await request.post('/recommendations/exercise')
    ElMessage.success('运动推荐生成成功')
    await loadHistory()
  } finally {
    exerciseLoading.value = false
  }
}

async function loadHistory() {
  history.value = await request.get('/recommendations/history')
}

function showDetail(row: any) {
  detailContent.value = row.content
  detailVisible.value = true
}

onMounted(loadHistory)
</script>
