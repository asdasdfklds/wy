import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '../layout/MainLayout.vue'
import Login from '../views/Login.vue'

const routes = [
    {
        path: '/',
        component: MainLayout, // 同步导入
        children: [
            {
                path: '/ticket/list',
                component: () => import('../views/TicketList.vue'), // 异步导入
                meta: {
                    requiredAuth: true
                }
            },
            {
                path: '/ticket/submit',
                component: () => import('../views/TicketSubmit.vue'),
                meta: {
                    requiredAuth: true
                }
            },
            {
                path: '/ticket/:id',
                component: () => import('../views/TicketDetail.vue'),
                meta: {
                    requiredAuth: true
                }
            },
            {
                path: '/knowledge',
                component: () => import('../views/KnowledgeManage.vue'),
                meta: {
                    requiredAuth: true,
                    adminOnly: true
                }
            },
            {
                path: '/chat',
                component: () => import('../views/ChatWindow.vue'),
                meta: {
                    requiredAuth: true
                }
            }
        ]
    },
    {
        path: '/login',
        component: Login
    }
]

const router = createRouter({
    routes,
    history: createWebHistory()
})

// 导航守卫
router.beforeEach((to, from, next) => {
    // 检查是否登录
   const token =localStorage.getItem('ticket_token')
   const user =localStorage.getItem('ticket_user')
   console.log(to, 'to')
   console.log(token, 'token')
   // 没有登录，访问内部页面需要跳转至登录首页
   if (to.meta.requiredAuth && !token) {
       return next('/login')
   }
   // 已经登录了就没必要再访问login
   if (to.path == '/login' && token) {
       return next('/ticket/list')
   }
   // 只有管理员才能访问知识库
   if (to.meta.adminOnly && user) {
       const u = JSON.parse(user)
       if (u.role !== 'admin') {
            return next('/ticket/list')
       }
   }
   next()
})

export default router