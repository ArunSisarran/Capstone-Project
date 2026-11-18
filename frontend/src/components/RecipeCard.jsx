import {Link} from 'react-router-dom';
import Card from '@mui/material/Card';
import Typography from '@mui/material/Typography';
import RestaurantRounded from '@mui/icons-material/RestaurantRounded';
import FavoriteButton from './FavoriteButton'
import SavedForLaterButton from './SavedForLaterButton'
import '../css/RecipeCard.css'
import {recordView} from '../utils/recordView.js'

const MAX_MISSING_SHOWN = 3;

const titleCase = (s) => s.charAt(0).toUpperCase() + s.slice(1);

// match fields only exist on /recipes/match results -Arun
function RecipeCard({recipe, favorites, setFavorites, savedforlater, setSavedForLater}){
    const isMatch = typeof recipe.matched_count === "number";
    const missing = (recipe.missing_ingredients || []).map((i) => i.name);
    const tags = (recipe.dietary_tags || []).map((t) => titleCase(t.name));
    const meta = [recipe.prep_time_minutes ? `${recipe.prep_time_minutes} min` : null, ...tags].filter(Boolean);

    return (
        <Card className="recipe-card">
            <div className="recipe-card__media">
                {recipe.image_url ? (
                    <img src={recipe.image_url} alt="" loading="lazy"/>
                ) : (
                    <span className="recipe-card__placeholder"><RestaurantRounded fontSize="inherit"/></span>
                )}
                {isMatch && (
                    <span className="recipe-card__badge">{recipe.matched_count} of {recipe.total_ingredients}</span>
                )}
                <div className="recipe-card__actions">
                    <FavoriteButton recipe={recipe} favorites={favorites} setFavorites={setFavorites}/>
                    <SavedForLaterButton recipe={recipe} savedforlater={savedforlater} setSavedForLater={setSavedForLater}/>
                </div>
            </div>

            <div className="recipe-card__body">
                {/* title link stretches over the card, see css -Arun */}
                <Typography variant="h3" component="h3" className="recipe-card__title">
                    <Link to={`/result/${recipe.id}`} onClick={() => recordView(recipe)}>{recipe.title}</Link>
                </Typography>
                {meta.length > 0 && <Typography variant="meta" component="p">{meta.join(" · ")}</Typography>}
                {isMatch && (missing.length === 0 ? (
                    <p className="recipe-card__status is-have">You have everything</p>
                ) : (
                    <p className="recipe-card__status is-miss">
                        Missing: {missing.slice(0, MAX_MISSING_SHOWN).join(", ")}
                        {missing.length > MAX_MISSING_SHOWN && ` +${missing.length - MAX_MISSING_SHOWN} more`}
                    </p>
                ))}
            </div>
        </Card>
    );
}

export default RecipeCard;
