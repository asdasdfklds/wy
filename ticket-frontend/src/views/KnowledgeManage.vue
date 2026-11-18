<!-- 知识库管理页 —— 新增表单 + 列表表格 -->
<template>
  <el-card>
    <!-- 标题与副标题 -->
    <h2>运维知识库管理</h2>
    <p style="color: #888">新增的知识会自动向量化存入 Milvus，作为 AI Agent 的参考资料</p>

    <!-- 新增表单 -->
    <el-form :model="form" label-width="80px" style="max-width: 720px; margin-top: 16px">
      <el-form-item label="标题">
        <el-input v-model="form.title" />
      </el-form-item>
      <el-form-item label="分类">
        <el-select v-model="form.category" placeholder="选填">
          <el-option label="网络" value="network" />
          <el-option label="硬件" value="hardware" />
          <el-option label="软件" value="software" />
          <el-option label="账号" value="account" />
        </el-select>
      </el-form-item>
      <el-form-item label="内容">
        <el-input v-model="form.content" type="textarea" :rows="4" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="onAdd">添加</el-button>
      </el-form-item>
    </el-form>

    <el-divider />

    <!-- 知识列表 -->
    <el-table :data="list" v-loading="loading" border>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="title" label="标题" />
      <el-table-column prop="category" label="分类" width="100" />
      <el-table-column prop="content" label="内容" show-overflow-tooltip />
      <el-table-column prop="createTime" label="创建时间" width="180" />
      <el-table-column label="操作" width="100">
        <template #default="{ row }">
          <el-popconfirm title="确定删除？" @confirm="onDelete(row.id)">
            <template #reference>
              <el-button size="small" type="danger">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { addKnowledge, listKnowledge, deleteKnowledge } from '@/api/knowledge'

// 新增表单
const form = ref({ title: '', content: '', category: '' })

// 列表数据 —— 演示数据写死，不调用接口
const list = ref([])

// 加载状态 —— 恒为 false
const loading = ref(false)

// 添加：本地插入，演示数据写死，不调用接口
const onAdd = async () => {
  if (!form.value.title || !form.value.content) {
    return ElMessage.warning('请填写标题和内容')
  }
  await addKnowledge(form.value)
  // const maxId = list.value.reduce((max, item) => Math.max(max, item.id), 0)
  // list.value.unshift({
  //   id: maxId + 1,
  //   title: form.value.title,
  //   category: form.value.category,
  //   content: form.value.content,
  //   createTime: '2026-10-24T10:00:00',
  // })
  load()
  ElMessage.success('已添加')
  form.value = { title: '', content: '', category: '' }
}

// 删除：本地过滤，演示数据写死，不调用接口
const onDelete = async (id) => {
  // list.value = list.value.filter((item) => item.id !== id)
  await deleteKnowledge(id)
  load()
  ElMessage.success('已删除')
}

// 数据写死，不调用接口
const load = async () => {
  loading.value = true
  try {
    const res = await listKnowledge()
    list.value = res
  } finally {
    loading.value = false
  }
}
onMounted(load)
</script>
