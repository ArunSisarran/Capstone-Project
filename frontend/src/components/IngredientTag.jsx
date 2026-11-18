import '../css/IngredientTag.css'

const CATEGORY_KEYS = {
    "Produce": "produce",
    "Dairy": "dairy",
    "Protein": "protein",
    "Grains / Starches": "grains",
    "Canned / Jarred / Packaged": "canned",
    "Condiments / Sauces": "condiments",
    "Baking / Pantry": "baking",
};

// matched=false: no recipe uses it yet -Arun
function IngredientTag({name, count = 1, category, matched = true}){
    const key = CATEGORY_KEYS[category] || category;
    const className = !matched ? "ingredient-tag is-off" : key ? `ingredient-tag cat-${key}` : "ingredient-tag";
    return (
        <span className={className} title={matched ? undefined : "No recipes use this yet"}>
            {name}
            {count > 1 && <span className="ingredient-tag__count">×{count}</span>}
        </span>
    );
}

export default IngredientTag;
