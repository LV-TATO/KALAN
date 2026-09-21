const BASE_URL = import.meta.env.VITE_API_BASE_URL

export class ApiError extends Error {
    constructor(status, detail) {
        super(
            typeof detail === 'string'
            ? detail
            : `Error ${status}`
        )

        this.name == 'ApiError'
        this.status = status
        this.detail = detail
    }
}

async function request(path, options = {}) {
    const headers = {
        ...options.headers,
    }

    if (options.body != null) {
        headers['Content-Type'] = 'application/json'
    }

    const response = await fetch(`${BASE_URL}${path}`,{
        ...options,
        headers,
    })

    if (!response.ok){
        let detail

        try{
            const data = await response.json()
            detail = data.detail
        } catch {
            detail = response.statusText
        }

        throw new ApiError(response.status,detail)
    }

    if (response.status === 204){
        return null
    }

    return response.json()
}

export const apiClient = {
  get: (path, options) =>
    request(path, {
      ...options,
      method: 'GET',
    }),

  post: (path, body, options) =>
    request(path, {
      ...options,
      method: 'POST',
      body: JSON.stringify(body),
    }),

  put: (path, body, options) =>
    request(path, {
      ...options,
      method: 'PUT',
      body: JSON.stringify(body),
    }),

  patch: (path, body, options) =>
    request(path, {
      ...options,
      method: 'PATCH',
      body: JSON.stringify(body),
    }),

  del: (path, options) =>
    request(path, {
      ...options,
      method: 'DELETE',
    }),
}