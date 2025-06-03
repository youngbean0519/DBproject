export async function apiFetch(path, options = {}) {
    const token = localStorage.jwt;
    const headers = {
        "Content-Type": "application/json",
        ...(options.headers || {})
    };
    if(token) headers.Authorization = `Bearer ${token}`;
    
    const res = await fetch(path, { ...options, headers });
    const text = await res.text();
    if(!res.ok) throw new Error(text);
    try { return JSON.parse(text); }
    catch { return text; }
}

export function showMessage(targetEl, msg, isError = false) {
    targetEl.textContent = msg;
    targetEl.className = isError ? "error" : "success";
}
