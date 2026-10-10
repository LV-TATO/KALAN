const BASE_URL = import.meta.env.VITE_API_BASE_URL
const AUTH_EXEMPT_PATHS = ['/api/v1/auth/login', '/api/v1/auth/register', '/api/v1/auth/refresh']

let accessToken = null
let sessionHandler = null
let refreshEnCurso = null

export class ApiError extends Error {
  constructor(status, detail, code) {
    super(detail || `Error ${status}`)
    this.status = status
    this.detail = detail
    this.code = code || 'ERROR'
  }
}

export function setAccessToken(token){
  accessToken = token
}

export function registerSessionHandler(handler){
  sessionHandler = handler
}

async function doFetch(path, options) {
  const headers = { 'Content-Type': 'application/json', ...options.headerss }
  if (accessToken) headers['Authorization'] = `Bearer ${accessToken}`
  return fetch(`${BASE_URL}${path}`, {...options, headers, credentials: 'include'})
}

async function parseErrorBody(response) {
  try {
    const body = await response.json()

    let detail = body.detail

    if (Array.isArray(detail)) {
      detail = detail
        .map((error) => {
          const campo = error.loc?.slice(1).join('.') || 'Solicitud'
          const mensaje = error.msg || 'Valor inválido'

          return `${campo}: ${mensaje}`
        })
        .join('\n')
    }

    if (typeof detail !== 'string') {
      detail = `Error ${response.status}`
    }

    return {
      detail,
      code: body.code || 'ERROR'
    }
  } catch {
    return {
      detail: response.statusText || `Error ${response.status}`,
      code: 'ERROR'
    }
  }
}

function attemptRefresh() {
  if (!refreshEnCurso) {
    refreshEnCurso = doFetch('/api/v1/auth/refresh', {method: 'POST'})
    .then(async (response) => {
      if (!response.ok){
        const {code} = await parseErrorBody(response)
        throw new ApiError(response.status, 'No se pudo renovar la sesion', code)
      }
      const data = await response.json()
      setAccessToken(data.access_token)
      return data.access_token
    })
    .finally(() => {refreshEnCurso = null})
  }
  return refreshEnCurso
}

async function request(path, options = {}, isRetry = false) {
  const response = await doFetch(path, options)

  if (response.ok){
    if (response.status === 204) return null
    return response.json()
  }
  
  const {detail, code} = await parseErrorBody(response)
  const isExempt = AUTH_EXEMPT_PATHS.some((p) => path.startWith(p))

  if (response.status === 401 && !isExempt && !isRetry){
    if (code === 'USER_BLOCKED'){
      setAccessToken(null)
      if (sessionHandler) sessionHandler(code)
        throw new ApiError(response.status, detail, code)
    }
    try{
      await attemptRefresh()
      return request(path, options, true)
    }catch (refreshError){
      setAccessToken(null)
      if (sessionHandler) sessionHandler(refreshError.code || 'SESION_INVALID')
        throw refreshError
    }
  }

  if (response.status == 401 && isRetry){
    setAccessToken(null)
    if (sessionHandler) sessionHandler(code)
  }

  throw new ApiError(response.status, detail, code)
}

export const apiClient = {
  get: (path, options) => request(path, { ...options, method: 'GET' }),
  post: (path, body, options) => request(path, { ...options, method: 'POST', body: body !== undefined ? JSON.stringify(body) : undefined }),
  put: (path, body, options) => request(path, { ...options, method: 'PUT', body: JSON.stringify(body) }),
  patch: (path, body, options) => request(path, { ...options, method: 'PATCH', body: JSON.stringify(body) }),
  del: (path, options) => request(path, { ...options, method: 'DELETE' }),
}