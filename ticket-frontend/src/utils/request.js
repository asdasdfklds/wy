import axios from "axios";
import { ElMessage } from 'element-plus'

const TOKEN_KEY = 'ticket_token'
const USER_KEY = 'ticket_user'

// 创建一个axios的实例
const request = axios.create({
    baseURL: '/api',
    timeout: 60000
})

// 清除本地登录状态
export function clearLogin() {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
}

// 请求拦截器
request.interceptors.request.use(function (config) {
    // 认证参数
    const token = localStorage.getItem(TOKEN_KEY)
    if (token) {
        config.headers['Authorization'] = 'Bearer ' + token
    }
    return config;
  }, function (error) {
    // Do something with request error
    return Promise.reject(error);
  });

// Add a response interceptor
request.interceptors.response.use(function (response) {
    const data = response.data
    // 状态码是否为200
    if (data.code === 200) {
        return data.data
    }
    ElMessage.error(data.msg || '请求失败')
  }, function (error) {
    // 获取http状态码
    const status = error.response?.status
    const msg = error.response?.data?.msg
    // 状态码为401
    if (status === 401) {
        // token无效或过期
        clearLogin()
        ElMessage.error(msg || '登录过期，请重新登录')
        import('../router').then(r => {
            if (r.default.currentRoute.value.path !== '/login') {
                r.default.push('/login')
            }
        })
    }
    // 其他状态码
    ElMessage.error(msg || '网络异常')
    return Promise.reject(error);
  });

export default request