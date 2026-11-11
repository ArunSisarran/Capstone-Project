import React, {useEffect, useState} from 'react'
import {useNavigate} from 'react-router-dom';
import {Link} from 'react-router-dom'
import '../css/Profile.css'
import Divider from '@mui/material/Divider';
import FavoriteButton from '../components/FavoriteButton'
import SavedForLaterButton from '../components/SavedForLaterButton'
import RecipeCard from '../components/RecipeCard'
import ProfileSideBar from '../components/ProfileSideBar'
import FavoritePage from '../components/FavoritePage'
import SavedForLaterPage from '../components/SavedForLaterPage' 

function Profile({history,setHistory,favorites,setFavorites,savedforlater,setSavedForLater}){

 const label = { slotProps: { input: { 'aria-label': 'Checkbox demo' } } };

    useEffect(() =>{
    const viewed = JSON.parse(localStorage.getItem("clickHistory") || "[]") //empty list if nothing viewed yet -Arun
    setHistory(viewed);
    },[]);

    return(
        <div className = "profile-page">
            <div className = "track-list">
                <div className="history">
                    <h1>Recent History </h1>
                    <Divider sx={{backgroundColor:"rgb(89,54,45)"}} />
                    {history.length === 0 ?(
                        <p>Empty History</p>
                    ):(
                  history.map((recipe)=>(
                        <div className ="history-info" key={recipe.id}>
                            <span className="time-title">
                            <p>{new Date(recipe.viewedAt).toLocaleDateString("en-US")}</p>
                            <Link to={`/result/${recipe.id}`} className="link">{recipe.title} </Link>
                            </span>
                            <span className= "info-buttons">
                            <FavoriteButton recipe={recipe} favorites={favorites} setFavorites={setFavorites}/>
                            <SavedForLaterButton recipe={recipe} savedforlater={savedforlater} setSavedForLater={setSavedForLater} />
                            </span>
                        </div>
                        ))
                    )}

                    
                </div> 
                    <Divider orientation="vertical" flexItem sx={{backgroundColor:"rgb(89,54,45)"}} />    
                    <ProfileSideBar />
            </div>
        </div>
    );
}

export default Profile;