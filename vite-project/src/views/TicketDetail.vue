<!-- 工单详情页 —— 顶部返回 + 描述表 + AI 建议 + 相似工单/知识库 -->
<template>
  <el-card v-loading="loading">
    <div v-if="ticket">
      <!-- 顶部返回行 -->
      <el-page-header  @back="$router.back()" style="margin-bottom: 16px">
        <template #content>
          <span style="font-size: 18px; font-weight: 600">工单 #{{ ticket.id }} - {{ ticket.title }}</span>
        </template>
      </el-page-header>

      <!-- 基本信息：两列带边框描述表 -->
      <el-descriptions :column="2" border>
        <el-descriptions-item label="故障类型">
          <el-tag>{{ ticket.faultType || '未识别' }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <!-- 管理员视角：直接渲染状态下拉框 -->
          <el-select v-if="isAdmin" v-model="ticket.status" @change="onSave">
            <el-option label="待处理" value="PENDING" />
            <el-option label="处理中" value="PROCESSING" />
            <el-option label="已解决" value="RESOLVED" />
            <el-option label="已关闭" value="CLOSED" />
          </el-select>
          <!-- 非管理员视角：只读显示 -->
          <span v-else>{{ statusLabel[ticket.status] }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="提交人ID">{{ ticket.submitterId }}</el-descriptions-item>
        <el-descriptions-item label="提交时间">{{ ticket.createTime }}</el-descriptions-item>
        <el-descriptions-item label="故障描述" :span="2">
          {{ ticket.description }}
        </el-descriptions-item>
        <el-descriptions-item label="处理结果" :span="2">
          <el-input
            v-if="isAdmin"
            v-model="resolution"
            type="textarea"
            :rows="3"
            placeholder="请填写处理结果"
            @blur="onSave"
          />
          <!-- 非管理员视角：只读显示 -->
          <span v-else>{{ resolution }}</span>
        </el-descriptions-item>
      </el-descriptions>

      <el-divider />

      <!-- AI 初步建议 -->
      <h3>🤖 AI 初步建议</h3>
      <el-alert
        v-if="ticket.aiSuggestion"
        :title="ticket.aiSuggestion"
        type="info"
        :closable="false"
        show-icon
      />

      <!-- 相似历史工单 -->
      <h3 style="margin-top: 24px">📎 相似历史工单</h3>
      <div v-if="similarTickets.length">
        <el-card
          v-for="s in similarTickets"
          :key="'t-' + s.id"
          shadow="never"
          style="margin-bottom: 8px"
        >
          <div style="display: flex; justify-content: space-between; align-items: center">
            <div style="font-weight: 600">#{{ s.id }} {{ s.title }}</div>
            <el-tag size="small" type="warning">相似度 {{ s.score }}</el-tag>
          </div>
          <div style="color: #666; margin-top: 6px; line-height: 1.6">{{ s.content }}</div>
        </el-card>
      </div>
      <el-empty v-else description="暂无相似历史工单（可多提交几条工单试试）" :image-size="80" />

      <!-- 知识库参考 -->
      <h3 style="margin-top: 24px">📚 知识库参考</h3>
      <div v-if="similarKnowledge.length">
        <el-card
          v-for="s in similarKnowledge"
          :key="'k-' + s.id"
          shadow="never"
          style="margin-bottom: 8px"
        >
          <div style="display: flex; justify-content: space-between; align-items: center">
            <div style="font-weight: 600">{{ s.title }}</div>
            <el-tag size="small" type="success">相似度 {{ s.score }}</el-tag>
          </div>
          <div style="color: #666; margin-top: 6px; line-height: 1.6; white-space: pre-line">{{ s.content }}</div>
        </el-card>
      </div>
      <el-empty v-else description="暂无知识库命中" :image-size="80" />
    </div>
  </el-card>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoute } from 'vue-router'
import { getTicket, updateTicket } from '@/api/ticket'

const route = useRoute()

// 状态/分类 中文映射
const statusLabel = { PENDING: '待处理', PROCESSING: '处理中', RESOLVED: '已解决', CLOSED: '已关闭' }
const statusTag = { PENDING: 'warning', PROCESSING: 'primary', RESOLVED: 'success', CLOSED: 'info' }
const categoryLabel = { network: '网络', hardware: '硬件', software: '软件', account: '账号' }

// 管理员视角写死 —— 演示数据不读取角色
const user = JSON.parse(localStorage.getItem('ticket_user') || '{}')
const isAdmin = computed(() => user?.role === 'admin')

// 演示数据写死，不调用接口、不读取路由与 localStorage
const ticket = ref({})

// 处理结果 —— 独立 ref
const resolution = ref('')

// 加载状态 —— 恒为 false
const loading = ref(false)

// 解析相似历史工单（后端返回 JSON 字符串）
const similarTickets = computed(() => {
  try {
    return JSON.parse(ticket.value.similarTickets || '[]')
  } catch (e) {
    return []
  }
})

// 解析知识库参考（后端返回 JSON 字符串）
const similarKnowledge = computed(() => {
  try {
    return JSON.parse(ticket.value.similarKnowledge || '[]')
  } catch (e) {
    return []
  }
})

// 保存处理结果 —— 演示数据写死，不调用接口
const onSave = async () => {
  try {
    await updateTicket(route.params.id, {
      status: ticket.value.status,
      resolution: resolution.value,
    })
    ElMessage.success('已保存')
  } catch (e) {
    ElMessage.error('保存工单失败')
  }
}

const load = async () => {
  loading.value = true
  try {
    const res = await getTicket(route.params.id)
    console.log(res, 'res')
    ticket.value = res
    // 初始化处理结果为工单当前处理结果
    resolution.value = res.resolution || ''
  } catch (e) {
    ElMessage.error('获取工单详情失败')
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>
