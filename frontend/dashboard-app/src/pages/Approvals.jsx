import React, { useEffect, useState } from 'react'
import { listPendingToolcalls, approveToolcall } from '../api'

export default function Approvals(){
  const [calls, setCalls] = useState([])
  const [loading, setLoading] = useState(false)
  const [msg, setMsg] = useState(null)

  useEffect(()=>{ fetchCalls() }, [])
  async function fetchCalls(){
    setLoading(true)
    try{
      const r = await listPendingToolcalls()
      setCalls(r)
    }catch(e){
      setMsg('Failed to load pending toolcalls')
    }finally{setLoading(false)}
  }

  async function doApprove(id){
    setMsg(null)
    try{
      await approveToolcall(id)
      setMsg('Approved successfully')
      fetchCalls()
    }catch(e){
      setMsg('Approval failed: ' + (e?.response?.data?.error || e.message))
    }
  }

  return (
    <section className="mb-6">
      <h2 className="text-lg font-medium">Pending Approvals</h2>
      {msg && <div className="p-2 bg-yellow-100">{msg}</div>}
      {loading ? <p>Loading...</p> : (
        <ul>
          {calls.length===0 && <li className="text-sm text-gray-500">No pending toolcalls</li>}
          {calls.map(c=> (
            <li key={c.id} className="border p-2 my-2 rounded">
              <div><strong>{c.tool}</strong> (#{c.id})</div>
              <pre className="text-xs bg-gray-100 p-2 rounded mt-2">{JSON.stringify(c.arguments, null, 2)}</pre>
              <div className="mt-2">
                <button className="bg-green-600 text-white px-2 py-1 rounded" onClick={()=>doApprove(c.id)}>Approve</button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
