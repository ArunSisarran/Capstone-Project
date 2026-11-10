import React, {useState, useEffect} from 'react'
import '../css/Profile.css'
import Divider from '@mui/material/Divider';
import {Link} from 'react-router-dom'
import FavoriteButton from '../components/FavoriteButton'
import SavedForLaterButton from '../components/SavedForLaterButton'
import ProfileSideBar from '../components/ProfileSideBar'
import FavoriteRecipeCard from '../components/FavoriteRecipeCard'
import Grid from '@mui/material/Grid';
import {base_url} from '../api/api.js'

function FavoritePage({history, setHistory, favorites,setFavorites,savedforlater,setSavedForLater}){

    useEffect(() =>{
        const getFavoritesCards = async () =>{
            try{
                const savedToken = localStorage.getItem("token");

                const response = await fetch(
                    `${base_url}/saved-recipes?kind=favorite&skip=0&limit=20`,
                    {
                        method:"GET",
                        headers:{
                            Authorization:`Bearer ${savedToken}`,
                            "Content-Type": "application/json"
                        }
                    }
                )

                if (!response.ok){
                    throw new Error ("Failed to save favorite!");
                }

               const data = await response.json()
                console.log("API DATA", data)
               setFavorites(data);
            }catch (error){
                console.log(error.message);
            }
        };

        getFavoritesCards();
},[]);

    return (
         <div className = "profile-page">
             <div className = "track-list">
                <div className="favorites">
                    <h1>Favorite Recipes</h1>
                    <Divider sx={{backgroundColor:"rgb(89,54,45)"}} />
                    <div className = "card-section">
                    {favorites.length === 0 ?(
                        <p>Empty Favorites</p>
                    ):(    
                                        <Grid container spacing = {2} sx ={{p:2, width:"100%", boxSizing:"border-box"}}>   
                 {favorites.map((recipe)=>(
                        <Grid recipe size={{xs:12,sm:6,md:4}} key={recipe.recipe_id}>
                                <FavoriteRecipeCard 
                                    recipe={recipe.recipe} 
                                    history = {history}
                                    setHistory = {setHistory}
                                    favorites = {favorites} 
                                    setFavorites = {setFavorites}
                                    savedforlater = {savedforlater}
                                    setSavedForLater = {setSavedForLater}
                                />
                        </Grid>
                   
                        ))}
                           </Grid>
                    )}
                                     
                     </div>
            </div>
                <Divider 
                    orientation="vertical" 
                    flexItem 
                    sx={{backgroundColor:"rgb(89,54,45)"}} 
                /> 
                <ProfileSideBar 
                />
        </div>
    </div>
    )
}

export default FavoritePage;