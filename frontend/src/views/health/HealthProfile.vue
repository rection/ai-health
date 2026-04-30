<template>
  <el-card>
    <template #header>个人健康档案</template>
    <el-form :model="form" label-width="120px" style="max-width: 600px">
      <el-form-item label="身高(cm)">
        <el-input-number v-model="form.height_cm" :min="50" :max="250" :precision="1" />
      </el-form-item>
      <el-form-item label="体重(kg)">
        <el-input-number v-model="form.weight_kg" :min="20" :max="300" :precision="1" />
      </el-form-item>
      <el-form-item label="生日">
        <el-date-picker v-model="form.birthday" type="date" value-format="YYYY-MM-DD" />
      </el-form-item>
      <el-form-item label="性别">
        <el-radio-group v-model="form.gender">
          <el-radio value="male">男</el-radio>
          <el-radio value="female">女</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="病史">
        <el-select v-model="form.diseases" multiple filterable allow-create placeholder="选择或输入病史" style="width: 100%">
          <el-option label="糖尿病" value="糖尿病" />
          <el-option label="高血压" value="高血压" />
          <el-option label="高血脂" value="高血脂" />
          <el-option label="痛风" value="痛风" />
          <el-option label="心脏病" value="心脏病" />
          <el-option label="肾病" value="肾病" />
          <el-option label="胃病" value="胃病" />
        </el-select>
      </el-form-item>
      <el-form-item label="过敏信息">
        <el-select v-model="form.allergies" multiple filterable allow-create placeholder="选择或输入过敏原" style="width: 100%">
          <el-option label="花生" value="花生" />
          <el-option label="牛奶" value="牛奶" />
          <el-option label="鸡蛋" value="鸡蛋" />
          <el-option label="海鲜" value="海鲜" />
          <el-option label="小麦" value="小麦" />
          <el-option label="大豆" value="大豆" />
        </el-select>
      </el-form-item>
      <el-form-item label="饮食偏好">
        <el-select v-model="form.dietary_preferences" multiple placeholder="选择饮食偏好" style="width: 100%">
          <el-option label="素食" value="素食" />
          <el-option label="低碳水" value="低碳水" />
          <el-option label="高蛋白" value="高蛋白" />
          <el-option label="低脂" value="低脂" />
          <el-option label="无糖" value="无糖" />
        </el-select>
      </el-form-item>
      <el-form-item v-if="form.gender === 'female'" label="生理期开始">
        <el-date-picker v-model="form.menstrual_cycle_start" type="date" value-format="YYYY-MM-DD" />
      </el-form-item>
      <el-form-item v-if="form.gender === 'female'" label="周期天数">
        <el-input-number v-model="form.menstrual_cycle_length" :min="21" :max="40" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import request from '../../api/request'
import { useUserStore } from '../../stores/user'
import { ElMessage } from 'element-plus'

const userStore = useUserStore()
const saving = ref(false)

const form = reactive({
  height_cm: null as number | null,
  weight_kg: null as number | null,
  birthday: null as string | null,
  gender: null as string | null,
  diseases: [] as string[],
  allergies: [] as string[],
  dietary_preferences: [] as string[],
  menstrual_cycle_start: null as string | null,
  menstrual_cycle_length: 28,
})

onMounted(async () => {
  await userStore.fetchUser()
  if (userStore.user) {
    form.height_cm = userStore.user.height_cm as any
    form.weight_kg = userStore.user.weight_kg as any
    form.birthday = userStore.user.birthday
    form.gender = userStore.user.gender
  }
  try {
    const profile: any = await request.get('/health-profile')
    form.diseases = profile.diseases || []
    form.allergies = profile.allergies || []
    form.dietary_preferences = profile.dietary_preferences || []
    form.menstrual_cycle_start = profile.menstrual_cycle_start
    form.menstrual_cycle_length = profile.menstrual_cycle_length || 28
  } catch {}
})

async function save() {
  saving.value = true
  try {
    await request.put('/users/me', {
      height_cm: form.height_cm,
      weight_kg: form.weight_kg,
      birthday: form.birthday,
      gender: form.gender,
    })
    await request.put('/health-profile', {
      diseases: form.diseases,
      allergies: form.allergies,
      dietary_preferences: form.dietary_preferences,
      menstrual_cycle_start: form.menstrual_cycle_start,
      menstrual_cycle_length: form.menstrual_cycle_length,
    })
    await userStore.fetchUser()
    ElMessage.success('保存成功')
  } finally {
    saving.value = false
  }
}
</script>
