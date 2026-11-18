import {useEffect, useState} from 'react'
import {Link, useLocation} from 'react-router-dom'
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Chip from '@mui/material/Chip';
import Alert from '@mui/material/Alert';
import Drawer from '@mui/material/Drawer';
import Skeleton from '@mui/material/Skeleton';
import CheckRounded from '@mui/icons-material/CheckRounded';
import TuneRounded from '@mui/icons-material/TuneRounded';
import NoFoodRounded from '@mui/icons-material/NoFoodRounded';
import SearchOffRounded from '@mui/icons-material/SearchOffRounded';
import FilterAltOffRounded from '@mui/icons-material/FilterAltOffRounded';
import {base_url} from '../api/api.js'
import RecipeCard from '../components/RecipeCard'
import IngredientTag from '../components/IngredientTag'
import EmptyState from '../components/EmptyState'
import '../css/ResultPage.css'

// allergen -> backend ingredient names that contain it -Arun
const ALLERGENS = [
    {label: "Egg", names: ["egg"]},
    {label: "Dairy", names: ["milk", "cheese", "butter", "cream", "yogurt"]},
    {label: "Nuts", names: ["nuts"]},
    {label: "Soy", names: ["tofu"]},
    {label: "Wheat", names: ["bread", "pasta", "flour"]},
    {label: "Shellfish", names: ["shrimp"]},
    {label: "Fish", names: ["fish"]},
];

const titleCase = (s) => s.charAt(0).toUpperCase() + s.slice(1);
const toggle = (list, value) => list.includes(value) ? list.filter((v) => v !== value) : [...list, value];

function Filters({dietaryTags, diets, setDiets, allergens, setAllergens}){
    const chip = (label, on, onClick) => (
        <Chip key={label} label={label} clickable onClick={onClick}
              variant={on ? "filled" : "outlined"} color={on ? "primary" : "default"}
              icon={on ? <CheckRounded/> : undefined} aria-pressed={on}
              sx={on ? {bgcolor: "app.primarySoft", color: "app.primary", "&:hover": {bgcolor: "app.primarySoft"}} : undefined}/>
    );
    return (
        <div className="filters">
            <div className="filters__group">
                <Typography variant="h3" component="h3">Diet</Typography>
                <div className="filters__chips">
                    {dietaryTags.map((t) => chip(titleCase(t.name), diets.includes(t.name), () => setDiets(toggle(diets, t.name))))}
                </div>
            </div>
            <div className="filters__group">
                <Typography variant="h3" component="h3">Leave out</Typography>
                <div className="filters__chips">
                    {ALLERGENS.map((a) => chip(a.label, allergens.includes(a.label), () => setAllergens(toggle(allergens, a.label))))}
                </div>
                <Typography variant="meta" component="p">Checks the main ingredients only. Always read the full recipe.</Typography>
            </div>
            {(diets.length > 0 || allergens.length > 0) && (
                <Button variant="text" onClick={() => {setDiets([]); setAllergens([]);}}>Clear all</Button>
            )}
        </div>
    );
}

function ResultPage({favorites, setFavorites, savedforlater, setSavedForLater, result, setResult}) {
    // undefined when browsing -Arun
    const scan = useLocation().state;
    const scanItems = scan?.items;
    const [loaded, setLoaded] = useState({url: null, failed: false});
    const [dietaryTags, setDietaryTags] = useState([]);
    const [diets, setDiets] = useState([]);
    const [allergens, setAllergens] = useState([]);
    const [showFilters, setShowFilters] = useState(false);

    // null when the scan found nothing matchable -Arun
    const ids = [...new Set((scanItems || []).map((item) => item.ingredient_id).filter(Boolean))].sort((a, b) => a - b);
    const url = !scanItems ? `${base_url}/recipes?skip=0&limit=60`
        : ids.length ? `${base_url}/recipes/match?` + ids.map((id) => `ingredient_ids=${id}`).join("&")
        : null;

    useEffect(() => {
        if (!url) return;
        let live = true;
        fetch(url)
            .then((res) => res.ok ? res.json() : Promise.reject(res.status))
            .then((json) => { if (live){ setResult(json); setLoaded({url, failed: false}); } })
            .catch(() => { if (live){ setResult([]); setLoaded({url, failed: true}); } });
        return () => { live = false; };
    }, [url, setResult]);

    const loading = url !== null && loaded.url !== url;
    const failed = !loading && url !== null && loaded.failed;
    const recipes = url && !loading ? result : [];

    useEffect(() => {
        fetch(`${base_url}/dietary-tags`)
            .then((res) => res.ok ? res.json() : [])
            .then(setDietaryTags)
            .catch(() => setDietaryTags([]));
    }, []);

    const blocked = new Set(ALLERGENS.filter((a) => allergens.includes(a.label)).flatMap((a) => a.names));
    const shown = recipes.filter((recipe) =>
        diets.every((d) => recipe.dietary_tags.some((t) => t.name === d)) &&
        !recipe.ingredients.some((i) => blocked.has(i.name))
    );
    const filterCount = diets.length + allergens.length;
    const filterProps = {dietaryTags, diets, setDiets, allergens, setAllergens};

    let body;
    if (loading){
        body = (
            <div className="recipe-grid" aria-hidden="true">
                {Array.from({length: 6}, (_, i) => (
                    <div key={i} className="recipe-skeleton">
                        <Skeleton variant="rectangular" sx={{aspectRatio: "4 / 3", height: "auto"}}/>
                        <div className="recipe-skeleton__text"><Skeleton width="80%"/><Skeleton width="45%"/></div>
                    </div>
                ))}
            </div>
        );
    }else if (failed){
        body = <Alert severity="error">We couldn't load recipes. Check that the server is running, then refresh.</Alert>;
    }else if (scanItems && scanItems.length === 0){
        body = <EmptyState icon={<NoFoodRounded fontSize="inherit"/>} title="We couldn't spot any food"
                           text="Try a closer, brighter photo with the fridge door wide open."
                           action={<Button component={Link} to="/">Scan again</Button>}/>;
    }else if (recipes.length === 0){
        body = <EmptyState icon={<SearchOffRounded fontSize="inherit"/>} title="No recipes use these yet"
                           text="None of our recipes match what we found. Browse everything instead."
                           action={<Button component={Link} to="/result">Browse all recipes</Button>}/>;
    }else if (shown.length === 0){
        body = <EmptyState icon={<FilterAltOffRounded fontSize="inherit"/>} title="No recipes fit these filters"
                           text="Turn off a filter to see more recipes."
                           action={<Button variant="outlined" onClick={() => {setDiets([]); setAllergens([]);}}>Clear filters</Button>}/>;
    }else{
        body = (
            <div className="recipe-grid">
                {shown.map((recipe) => (
                    <RecipeCard key={recipe.id} recipe={recipe}
                                favorites={favorites} setFavorites={setFavorites}
                                savedforlater={savedforlater} setSavedForLater={setSavedForLater}/>
                ))}
            </div>
        );
    }

    return (
        <main className="results">
            <header className="results__head">
                <Typography variant="h1">{scanItems ? "Recipes for you" : "All recipes"}</Typography>
                <Typography variant="meta" component="p" aria-live="polite">
                    {loading ? "Finding recipes…" : `${shown.length} ${shown.length === 1 ? "recipe" : "recipes"}${scanItems ? ", best match first" : ""}`}
                </Typography>
            </header>

            {scanItems && scanItems.length > 0 && (
                <section className="panel results__ingredients" aria-labelledby="ingredients-title">
                    <div className="results__ingredients-head">
                        <Typography variant="h2" id="ingredients-title">Your ingredients</Typography>
                        <Button variant="text" component={Link} to="/">Scan again</Button>
                    </div>
                    <div className="results__chips">
                        {scanItems.map((item) => (
                            <IngredientTag key={item.name} name={item.name} count={item.count} matched={Boolean(item.ingredient_id)}/>
                        ))}
                    </div>
                    {scan.vlm === "unavailable" && (
                        <Alert severity="warning">Our detailed scanner was busy, so some items may be missing. Try scanning again in a minute.</Alert>
                    )}
                </section>
            )}

            <div className="results__layout">
                <aside className="panel results__filters" aria-label="Filters">
                    <Filters {...filterProps}/>
                </aside>
                <section className="results__list" aria-label="Recipes">
                    <Button variant="outlined" className="results__filter-button" startIcon={<TuneRounded/>}
                            onClick={() => setShowFilters(true)}>
                        Filters{filterCount > 0 ? ` (${filterCount})` : ""}
                    </Button>
                    {body}
                </section>
            </div>

            <Drawer anchor="bottom" open={showFilters} onClose={() => setShowFilters(false)}>
                <div className="results__sheet">
                    <Typography variant="h2">Filters</Typography>
                    <Filters {...filterProps}/>
                    <Button fullWidth size="large" onClick={() => setShowFilters(false)}>
                        Show {shown.length} {shown.length === 1 ? "recipe" : "recipes"}
                    </Button>
                </div>
            </Drawer>
        </main>
    );
}

export default ResultPage;
