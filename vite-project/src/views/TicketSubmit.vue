<!-- 提交工单页 —— 表单 + AI 分析结果区 -->
<template>
  <el-card>
    <!-- 标题与副标题 -->
    <h2>提交工单</h2>
    <p style="color: #888">提交后 AI Agent 会自动分析你的故障描述，并返回建议与相似历史工单</p>

    <!-- 提交表单 -->
    <el-form :model="form" label-width="100px" style="max-width: 760px; margin-top: 24px" v-loading="loading">
      <el-form-item label="故障类型">
        <el-select v-model="form.faultType" placeholder="若不确定可不选，AI 会自动识别">
          <el-option label="网络" value="network" />
          <el-option label="硬件" value="hardware" />
          <el-option label="软件" value="software" />
          <el-option label="账号" value="account" />
        </el-select>
      </el-form-item>
      <el-form-item label="标题" required>
        <el-input v-model="form.title" placeholder="如：电脑无法连接公司内网" />
      </el-form-item>
      <el-form-item label="故障描述" required>
        <el-input
          v-model="form.description"
          type="textarea"
          :rows="6"
          placeholder="详细描述现象、出现时间、已尝试的操作"
        />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :loading="loading" @click="onSubmit">提交并让 AI 分析</el-button>
        <el-button @click="form = { title: '', description: '', faultType: '' }">重置</el-button>
      </el-form-item>
    </el-form>

    <!-- AI 分析结果区：仅在提交后显示 -->
    <el-divider v-if="result" />
    <div v-if="result">
      <h3>🤖 AI 分析结果</h3>
      <p>故障类型：<el-tag>{{ result.fault_type }}</el-tag></p>

      <p>初步建议：</p>
      <el-alert :title="result.suggestion" type="info" :closable="false" show-icon />

      <h4 style="margin-top: 20px">📎 相似历史工单</h4>
      <el-table v-if="result.similar_tickets.length" :data="result.similar_tickets" border size="small">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="title" label="标题" />
        <el-table-column prop="content" label="内容片段" show-overflow-tooltip />
        <el-table-column prop="score" label="相似度" width="100" />
      </el-table>
      <el-empty v-else description="暂无相似历史工单" :image-size="60" />

      <h4 style="margin-top: 20px">📚 知识库参考</h4>
      <el-table v-if="result.similar_knowledge.length" :data="result.similar_knowledge" border size="small">
        <el-table-column prop="title" label="标题" />
        <el-table-column prop="content" label="内容片段" show-overflow-tooltip />
        <el-table-column prop="score" label="相似度" width="100" />
      </el-table>
      <el-empty v-else description="暂无知识库命中" :image-size="60" />
    </div>
  </el-card>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { submitTicket, getTicket } from '@/api/ticket'
import { useRouter } from 'vue-router'

const router = useRouter()

// 表单数据 —— 初始为空，由用户填写
const form = ref({ title: '', description: '', faultType: '' })

// 提交加载状态 —— 恒为 false，仅作按钮静态绑定
const loading = ref(false)

// AI 分析结果 —— 初始为空，结果区隐藏
const result = ref(null)

// 提交：非空校验后直接展示写死的演示数据，不调用接口
const onSubmit = async () => {
  if (!form.value.title || !form.value.description) {
    ElMessage.warning('请填写完整')
    return
  }
  const ticket = await submitTicket(form.value)
  const detail = await getTicket(ticket.id)
  console.log(detail)
  result.value = {
    fault_type: detail.faultType,
    suggestion: detail.aiSuggestion,
    similar_tickets: detail.similarTickets ? JSON.parse(detail.similarTickets) : [],
    similar_knowledge: detail.similarKnowledge ? JSON.parse(detail.similarKnowledge) : [],
  }

  // 演示数据写死，不调用接口
  // result.value = {
  //   fault_type: 'network',
  //   suggestion:
  //     '请先确认网线是否插好、网卡指示灯是否正常；随后执行 ipconfig /flushdns 清理 DNS 缓存，若仍无法打开网页，请将 DNS 改为 8.8.8.8 后重试。',
  //   similar_tickets: [
  //     { id: 4, title: '能连内网但打不开网页（DNS 异常）', content: '内网可访问，浏览器打开外网站点提示无法解析域名…', score: 0.93 },
  //     { id: 5, title: '能连内网但打不开网页（DNS 异常）', content: '重启路由器后依旧无法解析，ping 8.8.8.8 正常…', score: 0.87 },
  //   ],
  //   similar_knowledge: [
  //     { title: 'DNS 解析异常排查手册', content: '1. 检查 DNS 服务器配置；2. 刷新 DNS 缓存；3. 更换公共 DNS…', score: 0.91 },
  //     { title: '公司内网访问外网故障处理规范', content: '确认代理设置、检查防火墙策略与网关连通性…', score: 0.78 },
  //   ],
  // }
  ElMessage.success('工单已提交，工单号 #' + ticket.id)
  // 跳转到工单详情页
  setTimeout(() => {
    router.push(`/ticket/${ticket.id}`)
  }, 1200)
}
</script>
