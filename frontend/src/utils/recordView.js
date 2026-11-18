const readHistory = () => {
    try { return JSON.parse(localStorage.getItem("clickHistory") || "[]"); } catch { return []; }
};

export function recordView(recipe){
    const entry = {id: recipe.id, title: recipe.title, viewedAt: new Date().toISOString()};
    const history = readHistory().filter((item) => item.id !== recipe.id);
    localStorage.setItem("clickHistory", JSON.stringify([entry, ...history].slice(0, 10)));
}

export {readHistory};
