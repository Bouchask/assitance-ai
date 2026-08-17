import React, { useEffect, useState } from 'react'
import Dashboard from './pages/Dashboard'
import Clients from './pages/Clients'
import Quotes from './pages/Quotes'
import Assignments from './pages/Assignments'
import Approvals from './pages/Approvals'
import Login from './pages/Login'
import { setAuthToken } from './api'

export default function App(){
  const [token, setToken] = useState(null)

  useEffect(()=>{
    const t = localStorage.getItem('api_token')
    if(t){ setAuthToken(t); setToken(t) }
  }, [])

  function onLogin(token){ setToken(token) }

  return (
    <div className="p-6 font-sans">
      <h1 className="text-2xl font-bold mb-4">Commercial Dashboard (Alpha)</h1>
      {!token ? (
        <Login onLogin={onLogin} />
      ) : (
        <div className="grid grid-cols-4 gap-4">
          <div className="col-span-1">
            <nav>
              <ul className="space-y-2">
                <li><a href="#dashboard" onClick={(e)=>{e.preventDefault(); window.scrollTo({top:0})}}>Dashboard</a></li>
                <li><a href="#clients" onClick={(e)=>{e.preventDefault(); document.getElementById('clients')?.scrollIntoView()}}>Clients</a></li>
                <li><a href="#quotes" onClick={(e)=>{e.preventDefault(); document.getElementById('quotes')?.scrollIntoView()}}>Quotes</a></li>
                <li><a href="#assignments" onClick={(e)=>{e.preventDefault(); document.getElementById('assignments')?.scrollIntoView()}}>Assignments</a></li>
                <li><a href="#approvals" onClick={(e)=>{e.preventDefault(); document.getElementById('approvals')?.scrollIntoView()}}>Approvals</a></li>
                <li><a href="#" onClick={(e)=>{e.preventDefault(); localStorage.removeItem('api_token'); setAuthToken(null); window.location.reload()}}>Logout</a></li>
              </ul>
            </nav>
          </div>
          <div className="col-span-3">
            <section id="dashboard"><Dashboard /></section>
            <section id="clients"><Clients /></section>
            <section id="quotes"><Quotes /></section>
            <section id="assignments"><Assignments /></section>
            <section id="approvals"><Approvals /></section>
          </div>
        </div>
      )}
    </div>
  )
}
