import { useState } from "react";
import { useNavigate } from "react-router";
import { useAuth } from "../../hooks/useAuth";

export default function Register() {
    const { register } = useAuth()
    const navigate = useNavigate()
    const [form, setForm] = useState({ email: '', password: '', nombre: '', zona: '' })
    const [error, setError] = useState(null)
    const [enviado, setEnviado] = useState(false)

    function handleChange(e) {
        setForm({ ...form, [e.target.name]: e.target.value })
    }

    async function handleSumbit(e) {
        e.preventDefault()
        setError(null)
        setEnviado(true)
        try {
            await register(form)
            navigate('/')
        } catch (err) {
            setError(err.detail || 'No se pudo completar el registro')
        } finally {
            setEnviado(false)
        }
    }

    return (
        <div className="mx-auto max-w-sm px-6 py-16">
            <h1 className="font-heading text-2xl text-kalan-primary">Crear Cuenta</h1>
            <form onSubmit={handleSumbit} className="mt-6 flex flex-col gap-4">
                <input name="nombre" placeholder="Nombre Completo" value={form.nombre}
                    onChange={handleChange} required className="rounded border border-kalan-accent px-3 py-2" />
                <input name="email" type="email" placeholder="Correo electrónico" value={form.email}
                    onChange={handleChange} required className="rounded border border-kalan-accent px-3 py-2" />
                <input name="password" type="password" placeholder="Contraseña" value={form.password}
                    onChange={handleChange} required minLength={8} className="rounded border border-kalan-accent px-3 py-2" />
                <input name="zona" placeholder="Zona (opcional)" value={form.zona}
                    onChange={handleChange} className="rounded border border-kalan-accent px-3 py-2" />
                {error && <p className="text-sm text-red-600">{error}</p>}
                <button type="submit" disabled={enviado}
                    className="rounded bg-kalan-primary px-4 py-2 text-kalan-cream disabled:opacity-50">
                    {enviado ? 'Creando cuenta...' : 'Registrarme'}
                </button>
            </form>
        </div>
    )
}