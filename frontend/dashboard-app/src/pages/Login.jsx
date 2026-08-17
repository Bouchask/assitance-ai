import React, { useState } from 'react'
import { login, setAuthToken } from '../api'

export default function Login({ onLogin }){
  const [email, setEmail] = useState('agent1@example.test')
  const [password, setPassword] = useState('password')
  const [error, setError] = useState(null)

  async function doLogin(e){
    e.preventDefault()
    setError(null)
    try{
      const res = await login(email, password)
      if(res && res.token){
        setAuthToken(res.token)
        localStorage.setItem('api_token', res.token)
        onLogin(res.token)
      } else {
        setError('No token in response')
      }
    }catch(err){
      setError(err?.response?.data?.error || err.message)
    }
  }

  return (
    <div className="p-4 border rounded mb-4">
      <h3 className="font-semibold mb-2">Login</h3>
      <form onSubmit={doLogin}>
        <div className="mb-2">
          <input className="border p-2 w-full" value={email} onChange={e=>setEmail(e.target.value)} placeholder="email" />
        </div>
        <div className="mb-2">
          <input className="border p-2 w-full" value={password} type="password" onChange={e=>setPassword(e.target.value)} placeholder="password" />
        </div>
        <div className="flex items-center gap-2">
          <button className="bg-blue-600 text-white px-3 py-1 rounded">Login</button>
          {error && <span className="text-red-600">{error}</span>}
        </div>
      </form>
    </div>
  )
}
