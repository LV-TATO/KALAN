import { useState } from "react";
import { useNavigate } from "react-router";
import { useAuth } from "../../hooks/useAuth";

export default function Login() {
    const { login } = useAuth()
    const navigate = useNavigate()
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState(null)
    const [enviado, setEnviado] = useState(false)

    async function handleSumbit(e) {
        e.preventDefault()
        setError(null)
        setEnviado(true)
        try {
            await login({ email, password })
            navigate('/')
        } catch (err) {
            setError(err.detail || 'No se pudo iniciar sesion')
        } finally {
            setEnviado(false)
        }
    }

    return (
        <div className="mx-auto max-w-sm px-6 py-16">
            <h1 className="font heading text-2x1 text-kalan-primary">Iniciar Sesión</h1>
            <form onSubmit={handleSumbit} className="mt-6 flex flex-col gap-4">
                <input type="email" placeholder="Correo Electrónico" value={email}
                    onChange={(e) => setEmail(e.target.value)} required
                    className="rounded border border-kalan-accent px-3 py-2" />
                <input type="password" placeholder="Contraseña" value={password}
                    onChange={(e) => setPassword(e.target.value)} required
                    className="rounded border border-kalan-accent px-3 py-2" />
                {error && <p className="text-sm text-red-600">{error}</p>}
                <button type="sumbit" disabled={enviado}
                    className="round bg-kalan-primary px-4 py-2 text-kalan-cream disabled:opacity-50">
                    {enviado ? 'Ingresando...' : 'Ingresar'}
                </button>
            </form>
        </div>
    )
}