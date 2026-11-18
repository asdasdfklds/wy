import request from '../utils/request'

export function listTickets(params) {
    return request.get('/ticket', { params })
}

export function submitTicket(data) {
    return request.post('/ticket', data)
}

export function getTicket(id) {
    return request.get(`/ticket/${id}`)
}

export function updateTicket(id, data) {
    return request.put(`/ticket/${id}`, data)
}
