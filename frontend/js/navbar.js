const links = [
    ["movies.html",    "🎬 영화"],
    ["likes.html",     "👍 좋아요"],
    ["watchlist.html", "📌 찜"],
    ["recommend.html", "⭐ 추천"],
    ["admin.html",     "🛠 Admin"]
];

const nav = document.createElement("nav");
nav.style.display = "flex";
nav.style.gap = "16px";
nav.style.marginBottom = "24px";
links.forEach(([href, text]) => {
    const a = Object.assign(document.createElement("a"), { href, textContent:text });
    if(location.pathname.endsWith(href)) a.style.fontWeight = "700";
    nav.appendChild(a);
});
document.body.prepend(nav);