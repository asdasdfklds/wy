<!-- 工单列表页 —— 标题行 + 搜索条件 + 表格 + 分页 -->
<template>
  <el-card>
    <!-- 头部行：左侧标题，右侧新建按钮 -->
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px">
      <h2 style="margin: 0">工单列表</h2>
      <el-button @click="$router.push('/ticket/submit')" type="primary">+ 新建工单</el-button>
    </div>

    <!-- 搜索条件：状态 + 提交时间范围 -->
    <el-form :inline="true" :model="query" class="search-bar">
      <el-form-item label="状态">
        <el-select v-model="query.status" placeholder="全部" clearable style="width: 160px">
          <el-option label="待处理" value="PENDING" />
          <el-option label="处理中" value="PROCESSING" />
          <el-option label="已解决" value="RESOLVED" />
          <el-option label="已关闭" value="CLOSED" />
        </el-select>
      </el-form-item>
      <el-form-item label="提交时间">
        <el-date-picker
          v-model="query.dateRange"
          type="daterange"
          value-format="YYYY-MM-DD"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          style="width: 260px"
        />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="onSearch">查询</el-button>
        <el-button @click="onReset">重置</el-button>
      </el-form-item>
    </el-form>

    <!-- 工单表格 -->
    <el-table :data="list" v-loading="loading" border>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="title" label="标题" />
      <el-table-column label="类型" width="100">
        <template #default="{ row }">
          <el-tag v-if="row.faultType" size="small">{{ row.faultType }}</el-tag>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="110">
        <template #default="{ row }">
          <el-tag :type="statusTag[row.status]" size="small">{{ statusLabel[row.status] }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="createTime" label="提交时间" width="180" />
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-button size="small" @click="$router.push(`/ticket/${row.id}`)">详情</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页：靠右 -->
    <el-pagination
      v-model:current-page="page"
      v-model:page-size="size"
      :page-sizes="[10, 20, 50]"
      layout="total, sizes, prev, pager, next"
      :total="total"
      style="margin-top: 16px; text-align: right"
    />
  </el-card>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { listTickets } from '@/api/ticket'

// 搜索表单：status 单选，dateRange 为 [开始日期, 结束日期]（YYYY-MM-DD）
const query = reactive({ status: '', dateRange: [] })

// 列表数据 —— 数据写死，不调用接口
const list = ref([])

// 分页与加载状态
const total = ref(6)
const page = ref(1)
const size = ref(10)
const loading = ref(false)

// 状态文案映射
const statusLabel = {
  PENDING: '待处理',
  PROCESSING: '处理中',
  RESOLVED: '已解决',
  CLOSED: '已关闭',
}

// 状态标签颜色映射
const statusTag = {
  PENDING: 'warning',
  PROCESSING: 'primary',
  RESOLVED: 'success',
  CLOSED: 'info',
}

// 查询 / 切换每页条数：回到第 1 页（数据写死，不重新拉取）
const onSearch = () => {
  page.value = 1
  load()
}

// 重置：清空搜索条件后触发查询
const onReset = () => {
  query.status = ''
  query.dateRange = []
  onSearch()
}

// 调用列表接口获取数据
const load = async () => {
  loading.value = true
  try {
    const [dateFrom, dateTo] = query.dateRange
    const res = await listTickets({
      page: page.value,
      size: size.value,
      status: query.status,
      dateFrom,
      dateTo,
    })
    list.value = res.list || []
    total.value = res.total || 0
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.search-bar {
  margin-bottom: 8px;
}
</style>
