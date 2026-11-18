import request from '../utils/request'

export function chat(data) {
    return request.post('/chat', data)
}