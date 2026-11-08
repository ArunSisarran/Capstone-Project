import React, {useState, useEffect} from 'react'
import '../css/Profile.css'
import Divider from '@mui/material/Divider';
import {Link} from 'react-router-dom'
import FavoriteButton from '../components/FavoriteButton'
import SavedForLaterButton from '../components/SavedForLaterButton'
import ProfileSideBar from '../components/ProfileSideBar'
import RecipeCard from '../components/RecipeCard'
import Grid from '@mui/material/Grid';


function FavoritePage({history, setHistory, favorites,setFavorites,savedforlater,setSavedForLater,token, setToken}){

    useEffect(() =>{
    const saved = JSON.parse(localStorage.getItem("clickFavorites"))
    setFavorites(saved);
    },[]);

    return (
         <div className = "profile-page">
             <div className = "track-list">
                <div className="favorites">
                    <h1>Favorite Recipes</h1>
                    <Divider sx={{backgroundColor:"rgb(89,54,45)"}} />
                    <div className = "card-section">
                    {favorites.length === 0 ?(
                        <p>Empty History</p>
                    ):(       
                  favorites.map((recipe)=>(
                    <Grid container spacing = {0} sx ={{p:3, width:"100%", boxSizing:"border-box"}}>
                        <Grid recipe size={20} key={recipe.id}>
                                <RecipeCard 
                                    recipe={recipe} 
                                    history = {history}
                                    setHistory = {setHistory}
                                    favorites = {favorites} 
                                    setFavorites = {setFavorites}
                                    savedforlater = {savedforlater}
                                    setSavedForLater = {setSavedForLater}
                                />
                        </Grid>
                    </Grid>
                   
                        ))
                    )}
                     </div>
            </div>
                <Divider 
                    orientation="vertical" 
                    flexItem 
                    sx={{backgroundColor:"rgb(89,54,45)"}} 
                /> 
                <ProfileSideBar 
                    token={token} 
                    setToken={setToken}
                />
        </div>
    </div>
    )
}

export default FavoritePage;