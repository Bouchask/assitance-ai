import React, {useEffect, useState} from 'react'
import { listClients } from '../api'

export default function Clients(){
  const [clients, setClients] = useState([])
  useEffect(()=>{ listClients().then(setClients).catch(()=>{}) }, [])
  return (
    <section className="mb-6">
      <h2 className="text-lg font-medium">Clients</h2>
      <ul>
        {clients.map(c=> <li key={c.id}>{c.name} — {c.email}</li>)}
      </ul>
    </section>
  )
}
