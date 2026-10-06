import { useEffect, useState } from 'react'
import { checkBackendHealth } from '../services/health'

export default function Home() {
  const [status, setStatus] = useState('checking')

  useEffect(() => {
    checkBackendHealth()
      .then(() => setStatus('ok'))
      .catch((err) => {
        console.error('No se pudo conectar con el backend:', err)
        setStatus('error')
      })
  }, [])

  return (
    <div className="px-6 py-16 text-center">
      <h1 className="font-heading text-3xl text-kalan-primary">Kalan</h1>
      <p className="mt-4 text-kalan-accent">
        {status === 'checking' && 'Comprobando conexión con el backend…'}
        {status === 'ok' && '✅ Backend conectado correctamente.'}
        {status === 'error' && '⚠️ No se pudo conectar con el backend.'}
      </p>
    </div>
  )
}