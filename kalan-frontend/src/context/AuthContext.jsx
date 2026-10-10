import { createContext, useCallback, useEffect, useState } from 'react'
import * as authService from '../services/auth'
import { registerSessionHandler, setAccessToken } from '../services/apiClient'

export const AuthContext = createContext(null)

export function AuthProvider({ children }) {
    const [usuario, setUsuario] = useState(null)
    const [estadoAuth, setEstadoAuth] = useState('cargando')
    const [bloqueado, setBloqueado] = useState(false)

    const limpiarSesion = useCallback((code) => {
        setAccessToken(null)
        setUsuario(null)
        setBloqueado(code === 'USER_BLOCKED')
        setEstadoAuth('no-autenticado')
    }, [])

    useEffect(() => {
        registerSessionHandler(limpiarSesion)
    }, [limpiarSesion])

    useEffect(() => {
        authService.refresh()
            .then(({ access_token }) => {
                setAccessToken(access_token)
                return authService.me()
            })
            .then((datosUsuario) => {
                setUsuario(datosUsuario)
                setBloqueado(false)
                setEstadoAuth('autenticado')
            })
            .catch((error) => {
                limpiarSesion(error.code)
            })
    }, [limpiarSesion])

    const login = useCallback(async (credenciales) => {
        const { access_token } = await authService.login(credenciales)
        setAccessToken(access_token)
        setUsuario(await authService.me())
        setBloqueado(false)
        setEstadoAuth('autenticado')
    }, [])

    const register = useCallback(async (datos) => {
        const { access_token } = await authService.register(datos)
        setAccessToken(access_token)
        setUsuario(await authService.me())
        setBloqueado(false)
        setEstadoAuth('autenticado')
    }, [])

    const logout = useCallback(async () => {
        try {
            await authService.logout()
        } catch (error) {
            console.error(
                'No se pudo confirmar el cierre de sesión en el servidor:',
                error
            )

            throw error
        } finally {
            limpiarSesion()
        }
    }, [limpiarSesion])

    return (
        <AuthContext.Provider value={{ usuario, estadoAuth, bloqueado, login, register, logout }}>
            {children}
        </AuthContext.Provider>
    )
}