export function apiFetch(path, options = {}) {
    const token = localStorage.getItem("jwt");
    const headers = { "Content-Type": "appication/json", ...(options.headers || {}) };
    if(token) headers["Authorization"] = `Bearer ${token}`;
    return fetch(path, { ...options, headers })
        .then(async res => {
            if(!res.ok) throw new Error((await res.json()).message || res.statusText);
            return res.json();
        });
}

export function showMessage(targetEl, msg, isError = false) {
    targetEl.textContent = msg;
    targetEl.className = isError ? "error" : "success";
}
