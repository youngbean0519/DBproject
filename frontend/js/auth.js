import { apiFetch, showMessage } from './utils.js';

function handleAuth(form, mode) {
    const msgEl = form.querySelector(".msg");
    
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        showMessage(msgEl, "Loading...");
        
        const raw = Object.fromEntries(new FormData(form));
        raw.notify_by_email = form.notify_by_email.checked;
        const body = JSON.stringify(raw);

        try {
            const data = await apiFetch(`/auth/${mode}`, {
                method: "POST",
                body
            });
            if(data.token) localStorage.jwt = data.token;
            showMessage(msgEl, `${mode} success!`);
        } catch(err) {
            showMessage(msgEl, err.message, true);
        }
    });
}

if(location.pathname.endsWith("login.html")) {
    handleAuth(document.querySelector("form"), "login");
}

if(location.pathname.endsWith("register.html")) {
    handleAuth(document.querySelector("form"), "register");
}