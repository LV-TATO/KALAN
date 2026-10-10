import { Outlet } from 'react-router'
import Navbar from '../components/Navbar'
import Footer from '../components/Footer'
import { useAuth } from '../hooks/useAuth'

export default function MainLayout() {
  const { bloqueado } = useAuth()
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      {bloqueado && (
        <div className='bg-red-600 px-6 py-2 text-center text-sm text-white'>
          Tu cuenta ha sido bloqueada por un administrador.
        </div>
      )}
      <main className="flex-1"><Outlet /></main>
      <footer />
    </div>
  )
}