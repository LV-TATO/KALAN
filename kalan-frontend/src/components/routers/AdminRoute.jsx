import { Navigate, Outlet } from "react-router";
import { useAuth } from "../../hooks/useAuth";

export default function AdminRoute(){
    const {estadoAuth, usuario} = useAuth()
    if (estadoAuth === 'cargando') return null
    if (estadoAuth === 'no-autenticado') return <Navigate to={"/login"} replace/>
    if (usuario?.rol !== 'admin') return <Navigate to={"/"} replace/>
    return <Outlet/>

}