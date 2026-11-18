import request from '@/utils/request'

export function addKnowledge(data) {
    return request.post('/knowledge', data)
}

export function listKnowledge(params) {
    return request.get('/knowledge', { params })
}

export function deleteKnowledge(id) {
    return request.delete(`/knowledge/${id}`)
}