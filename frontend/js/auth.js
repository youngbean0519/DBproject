import { apiFetch, showMessage } from './utils.js';

function handleAuth(form, mode) {
    const msgEl = form.querySelector(".msg");
    form.addEventListener("submit", e => {
        e.preventDefault();
        showMessage(msgEl, "Loading...");
        const body = Object.fromEntries(new FormData(form));
        apiFetch(`/auth/${mode}`, {
            method: "POST",
            body: JSON.stringify(body),
        })
        .then(data => {
            if(data.token) localStorage.setItem("jwt", data.token);
            showMessage(msgEl, `${mode} success!`);
            setTimeout(() => window.location.href = "index.html", 800);
        })
        .catch(err => showMessage(msgEl, err.message, true));
    });
}

if(location.pathname.endsWith("login.html")) {
    handleAuth(document.querySelector("form", "login"));
}

if(location.pathname.endsWith("register.html")) {
    handleAuth(document.querySelector("form"), "register");
}