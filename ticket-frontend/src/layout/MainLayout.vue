<!-- 主布局组件 —— 左侧菜单 + 顶部 Header + 中间内容区 -->
<template>
  <!-- 外层容器：横向 flex，整体占满视口高度 -->
  <el-container style="height: 100vh">
    <!-- 左侧侧边栏：深色背景 + Logo + 导航菜单 -->
    <el-aside width="220px" style="background-color: #001529; color: #fff">
      <!-- 顶部 Logo 区 -->
      <div style="padding: 20px; font-size: 18px; text-align: center; color: #fff">
        运维工单Agent
      </div>

      <!-- 侧边导航菜单（router 模式，index 即跳转路径） -->
      <el-menu
        background-color="#001529"
        text-color="#fff"
        active-text-color="#ffd04b"
        router
        :default-active="route.path"
      >
        <el-menu-item index="/ticket/list">
          <el-icon><Document /></el-icon>
          <span>工单列表</span>
        </el-menu-item>
        <el-menu-item index="/ticket/submit">
          <el-icon><Edit /></el-icon>
          <span>提交工单</span>
        </el-menu-item>
        <!-- 知识库管理仅管理员可见 -->
        <el-menu-item v-if="isAdmin" index="/knowledge">
          <el-icon><Reading /></el-icon>
          <span>知识库管理</span>
        </el-menu-item>
        <el-menu-item index="/chat">
          <el-icon><ChatDotRound /></el-icon>
          <span>AI 助手</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- 内层容器：纵向 flex（Header + Main） -->
    <el-container style="flex-direction: column">
      <!-- 顶部 Header：左侧系统标题，右侧用户信息 + 退出登录 -->
      <el-header
        style="
          background-color: #fff;
          border-bottom: 1px solid #eee;
          display: flex;
          align-items: center;
          justify-content: space-between;
        "
      >
        <!-- 左侧：系统标题 -->
        <div style="font-weight: 600">📋 IT 运维智能工单系统</div>

        <!-- 右侧：用户信息 + 退出登录 -->
        <div style="display: flex; align-items: center">
          <el-tag>{{ user.realName }}（{{ isAdmin ? '管理员' : '普通用户' }}）</el-tag>
          <el-button type="text" style="margin-left: 12px" @click="onLogout">
            退出登录
          </el-button>
        </div>
      </el-header>

      <!-- 主内容区：浅灰背景，渲染子路由 -->
      <el-main style="background-color: #f0f2f5">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'

// 当前路由对象，用于菜单高亮当前路径
const route = useRoute()

// 路由实例，用于退出登录后跳转登录页
const router = useRouter()

// 用户信息 —— 直接写死，不调用任何接口
const user = JSON.parse(localStorage.getItem('ticket_user') || '{}')

// 是否管理员 —— 控制知识库管理菜单的显示
const isAdmin = user.role === 'admin'

// 退出登录 —— 二次确认后跳转登录页
const onLogout = () => {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(() => {
      localStorage.removeItem('ticket_token')
      localStorage.removeItem('ticket_user')
      router.push('/login')
    })
    .catch(() => {})
}
</script>
