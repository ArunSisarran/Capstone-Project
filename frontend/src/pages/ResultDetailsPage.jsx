import {useEffect, useState} from 'react'
import {Link, useNavigate, useParams} from 'react-router-dom'
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Chip from '@mui/material/Chip';
import Skeleton from '@mui/material/Skeleton';
import ArrowBackRounded from '@mui/icons-material/ArrowBackRounded';
import OpenInNewRounded from '@mui/icons-material/OpenInNewRounded';
import RestaurantRounded from '@mui/icons-material/RestaurantRounded';
import SearchOffRounded from '@mui/icons-material/SearchOffRounded';
import EmptyState from '../components/EmptyState'
import {parseRecipe} from '../utils/parseRecipe.js'
import {base_url} from '../api/api.js'
import '../css/ResultDetailsPage.css'

const titleCase = (s) => s.charAt(0).toUpperCase() + s.slice(1);

function ResultDetailsPage(){
    const {id} = useParams();
    const navigate = useNavigate();
    const [loaded, setLoaded] = useState({id: null, recipe: null});

    useEffect(() => {
        let live = true;
        fetch(`${base_url}/recipes/${id}`)
            .then((res) => res.ok ? res.json() : null)
            .catch(() => null)
            .then((recipe) => { if (live) setLoaded({id, recipe}); });
        return () => { live = false; };
    }, [id]);

    const goBack = () => window.history.length > 1 ? navigate(-1) : navigate("/result");
    const back = (
        <Button variant="text" startIcon={<ArrowBackRounded/>} onClick={goBack} className="recipe__back">Back</Button>
    );

    if (loaded.id !== id){
        return (
            <main className="page-shell recipe" aria-busy="true">
                {back}
                <Skeleton variant="rectangular" className="recipe__hero" sx={{height: "auto", borderRadius: "20px"}}/>
                <Skeleton width="60%" height={48}/>
                <Skeleton width="30%"/>
            </main>
        );
    }

    const recipe = loaded.recipe;
    if (!recipe){
        return (
            <main className="page-shell recipe">
                {back}
                <EmptyState icon={<SearchOffRounded fontSize="inherit"/>} title="We couldn't find that recipe"
                            text="It may have been removed, or the server isn't running."
                            action={<Button component={Link} to="/result">Browse all recipes</Button>}/>
            </main>
        );
    }

    const {ingredients, steps} = parseRecipe(recipe.instructions);
    const ingredientLines = ingredients.length ? ingredients : recipe.ingredients.map((i) => titleCase(i.name));

    return (
        <main className="page-shell recipe">
            {back}
            <article className="recipe__article">
                <div className="recipe__hero">
                    {recipe.image_url ? (
                        <img src={recipe.image_url} alt={recipe.title}/>
                    ) : (
                        <span className="recipe__placeholder"><RestaurantRounded fontSize="inherit"/></span>
                    )}
                </div>

                <header className="recipe__header">
                    <Typography variant="display" component="h1" className="recipe__title">{recipe.title}</Typography>
                    <div className="recipe__meta">
                        {recipe.prep_time_minutes ? <Chip label={`${recipe.prep_time_minutes} min`} variant="outlined"/> : null}
                        {recipe.dietary_tags.map((t) => (
                            <Chip key={t.id} label={titleCase(t.name)} sx={{bgcolor: "app.haveSoft", color: "app.have"}}/>
                        ))}
                        {recipe.source_url && (
                            <Button variant="text" href={recipe.source_url} target="_blank" rel="noreferrer" endIcon={<OpenInNewRounded/>}>
                                Original recipe
                            </Button>
                        )}
                    </div>
                </header>

                <div className="recipe__columns">
                    <section className="panel recipe__ingredients" aria-labelledby="ingredients-title">
                        <Typography variant="h2" id="ingredients-title">Ingredients</Typography>
                        <ul>
                            {ingredientLines.map((line, i) => <li key={i}>{line}</li>)}
                        </ul>
                    </section>

                    <section className="panel recipe__steps" aria-labelledby="steps-title">
                        <Typography variant="h2" id="steps-title">Steps</Typography>
                        <ol>
                            {steps.map((step, i) => <li key={i}>{step}</li>)}
                        </ol>
                    </section>
                </div>
            </article>
        </main>
    );
}

export default ResultDetailsPage;
