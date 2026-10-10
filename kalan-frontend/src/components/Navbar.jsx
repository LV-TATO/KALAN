import { Link } from "react-router";
import { useAuth } from "../hooks/useAuth";

export default function Navbar() {
  const { estadoAuth, usuario, logout } = useAuth()
  return (
    <header className="flex items-center justify-between bg-kalan-primary px-6 py-4 text-kalan-cream">
      <Link to="/" className="font-heading text-xl">Kalan</Link>
      <nav className="flex items-center gap-4 text-sm">
        {estadoAuth === 'autenticado' && (
          <>
          <span>{usuario?.nombre}</span>
          <button onClick={logout} className="underline">Cerrar sesión
          </button>
          </>
        )}
        {estadoAuth === 'no-autenticado' && (
          <>
          <Link to="/login">Iniciar sesión</Link>
          <Link to="/register">Registrarme</Link>
          </>
        )}
      </nav>
    </header>
  )
}