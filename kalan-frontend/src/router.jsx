import { createBrowserRouter } from "react-router";
import MainLayout from "./layouts/MainLayout";
import Home from './pages/Home'
import NotFound from './pages/NotFound'
import Login from "./pages/auth/Login";
import Register from "./pages/auth/Register";
import ProtectedRoute from "./components/routers/ProtecteRoute";
import AdminRoute from "./components/routers/AdminRoute";

export const router = createBrowserRouter([
  {
    path: '/',
    element: <MainLayout />,
    children: [
      { index: true, element: <Home /> },
      { path: 'login', element: <Login /> },
      { path: 'register', element: <Register /> },
      {element: <ProtectedRoute />, children: [
          //Rutas Protegidas
        ]},
      {
        element: <AdminRoute />, children: [
          // Rutas de administracion
        ]},
      { path: '*', element: <NotFound /> },
    ],
  },
])