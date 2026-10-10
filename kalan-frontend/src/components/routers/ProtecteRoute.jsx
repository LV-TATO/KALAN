import { Navigate, Outlet } from "react-router";
import { useAuth } from "../../hooks/useAuth";

export default function ProtectedRoute(){
    const {estadoAuth} = useAuth()
    if (estado === 'cargando') return null
    if (estadoAuth === 'no-autenticado') return <Navigate to="{/login}" replace/>
    return <Outlet/>
}