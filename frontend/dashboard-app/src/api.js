import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000/api'

export const api = axios.create({ baseURL: API_BASE })
let authToken = null

export function setAuthToken(token){
  authToken = token
  if(token){
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`
  } else {
    delete api.defaults.headers.common['Authorization']
  }
}

export async function login(email, password){
  const r = await api.post('/login', { email, password })
  return r.data
}

export async function listClients(){
  const r = await api.get('/clients')
  return r.data
}

export async function listQuotes(){
  const r = await api.get('/quotes')
  return r.data
}

export async function createQuote(payload){
  const r = await api.post('/quotes', payload)
  return r.data
}

export async function listPendingToolcalls(){
  const r = await api.get('/toolcalls/pending')
  return r.data
}

export async function approveToolcall(id){
  const r = await api.post(`/toolcalls/${id}/approve`)
  return r.data
}

export async function listAssignments(){
  const r = await api.get('/assignments')
  return r.data
}

export async function createAssignment(payload){
  const r = await api.post('/assignments', payload)
  return r.data
}

export async function sendQuote(quoteId){
  const r = await api.post(`/quotes/${quoteId}/send`)
  return r.data
}
