// lines like "step 1" are markers, not steps -Arun
const STEP_MARKER = /^(step\s*)?\d+\s*[.:)]?$/i;

// expects the import format: "ingredients:" list, then "instructions:" -Arun
export function parseRecipe(text = ""){
    const [head, body] = text.includes("Instructions:") ? text.split("Instructions:", 2) : ["", text];
    const ingredients = head.split("\n")
        .map((line) => line.trim())
        .filter((line) => line.startsWith("-"))
        .map((line) => line.replace(/^-\s*/, "").replace(/\s+/g, " "))
        .filter(Boolean);
    const steps = body.split("\n")
        .map((line) => line.trim())
        .filter((line) => line && !STEP_MARKER.test(line));
    return {ingredients, steps};
}
