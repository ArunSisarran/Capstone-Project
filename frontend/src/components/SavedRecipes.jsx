import {useEffect, useState} from 'react'
import {Link} from 'react-router-dom'
import Button from '@mui/material/Button';
import Skeleton from '@mui/material/Skeleton';
import Alert from '@mui/material/Alert';
import FavoriteRounded from '@mui/icons-material/FavoriteRounded';
import BookmarkRounded from '@mui/icons-material/BookmarkRounded';
import AccountLayout from './AccountLayout'
import RecipeCard from './RecipeCard'
import EmptyState from './EmptyState'
import {base_url} from '../api/api.js'

const COPY = {
    favorite: {icon: <FavoriteRounded fontSize="inherit"/>, title: "No favorites yet", text: "Tap the heart on a recipe to keep it here."},
    saved: {icon: <BookmarkRounded fontSize="inherit"/>, title: "Nothing saved yet", text: "Tap the bookmark on a recipe to save it for later."},
};

function SavedRecipes({kind, list, setList, favorites, setFavorites, savedforlater, setSavedForLater}){
    const [state, setState] = useState("loading");

    useEffect(() => {
        let live = true;
        (async () => {
            try{
                const response = await fetch(`${base_url}/saved-recipes?kind=${kind}&skip=0&limit=50`, {
                    headers: {Authorization: `Bearer ${localStorage.getItem("token")}`},
                });
                if (!response.ok) throw new Error(String(response.status));
                const data = await response.json();
                if (live){ setList(data); setState("ready"); }
            }catch{
                if (live) setState("failed");
            }
        })();
        return () => { live = false; };
    }, [kind, setList]);

    let body;
    if (state === "loading"){
        body = (
            <div className="recipe-grid" aria-hidden="true">
                {Array.from({length: 3}, (_, i) => <Skeleton key={i} variant="rounded" sx={{aspectRatio: "4 / 4", height: "auto", borderRadius: "16px"}}/>)}
            </div>
        );
    }else if (state === "failed"){
        body = <Alert severity="error">We couldn't load your recipes. Check that you're logged in and the server is running.</Alert>;
    }else if (list.length === 0){
        body = <EmptyState {...COPY[kind]} action={<Button component={Link} to="/result">Browse recipes</Button>}/>;
    }else{
        body = (
            <div className="recipe-grid">
                {list.map((item) => (
                    <RecipeCard key={item.recipe_id} recipe={item.recipe}
                                favorites={favorites} setFavorites={setFavorites}
                                savedforlater={savedforlater} setSavedForLater={setSavedForLater}/>
                ))}
            </div>
        );
    }

    return <AccountLayout>{body}</AccountLayout>;
}

export default SavedRecipes;
