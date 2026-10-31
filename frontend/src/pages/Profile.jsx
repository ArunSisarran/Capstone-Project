import React from 'react'
import {useEffect, useState} from 'react'
import { Link} from 'react-router-dom'
import '../css/Profile.css'
import Divider from '@mui/material/Divider';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import FavoriteButton from '../components/FavoriteButton'
import SavedForLaterButton from '../components/SavedForLaterButton'
import RecipeCard from '../components/RecipeCard'

function Profile({history,setHistory,favorites,setFavorites,savedforlater,setSavedForLater}){
 const label = { slotProps: { input: { 'aria-label': 'Checkbox demo' } } };

    useEffect(() =>{
    const viewed = JSON.parse(localStorage.getItem("clickHistory"))
    setHistory(viewed);
    },[]);

    useEffect(() =>{
    const saved = JSON.parse(localStorage.getItem("clickFavorites"))
    setFavorites(saved);
    },[]);

     useEffect(() =>{
    const later = JSON.parse(localStorage.getItem("clickSaved")) || [];
     setSavedForLater(later);
    },[]);

    return(
        <div className = "profile-page">
            <div className="track-list">
                <div className="history">
                    <h1>Recent History </h1>
                    <Divider sx={{backgroundColor:"rgb(89,54,45)"}} />
                    {history.length === 0 ?(
                        <p>Empty History</p>
                    ):(
                  history.map((recipe)=>(
                        <div className ="history-info" key={recipe.id}>
                            <span>
                            <p>{new Date(recipe.viewedAt).toLocaleDateString("en-US")}</p>
                            <Link to={`/result/${recipe.id}`} className="link">{recipe.title} </Link>
                            </span>
                            <FavoriteButton recipe={recipe} favorites={favorites} setFavorites={setFavorites}/>
                            <SavedForLaterButton recipe={recipe} savedforlater={savedforlater} setSavedForLater={setSavedForLater} />
                        </div>
                        ))
                    )}

                </div>

                <div className="favorites">
                    <h1>Favorite Recipes</h1>
                    <Divider sx={{backgroundColor:"rgb(89,54,45)"}} />
                    {favorites.length === 0 ?(
                        <p>Empty History</p>
                    ):(
                  favorites.map((recipe)=>(
                        <div className ="history-info" key={recipe.id}>
                            <span>
                            <p>{new Date(recipe.viewedAt).toLocaleDateString("en-US")}</p>
                            <Link to={`/result/${recipe.id}`} className="link">{recipe.title} </Link>
                            </span>
                            <FavoriteButton recipe={recipe} favorites={favorites} setFavorites={setFavorites}/>
                            <SavedForLaterButton recipe={recipe} savedforlater={savedforlater} setSavedForLater={setSavedForLater} />
                        </div>
                        ))
                    )}
                </div>

                <div className="SavedForLater">
                    <h1>Saved For Later </h1>
                    <Divider sx={{backgroundColor:"rgb(89,54,45)"}} />
                    {savedforlater.length === 0 ?(
                        <p>Empty History</p>
                    ):(
                    savedforlater.map((recipe)=>(
                        <div className ="history-info" key={recipe.id}>
                            <span>
                            <p>{new Date(recipe.viewedAt).toLocaleDateString("en-US")}</p>
                            <Link to={`/result/${recipe.id}`} className="link">{recipe.title} </Link>
                            </span>
                            <FavoriteButton recipe={recipe} favorites={favorites} setFavorites={setFavorites}/>
                            <SavedForLaterButton recipe={recipe} savedforlater={savedforlater} setSavedForLater={setSavedForLater} />
                        </div>
                        ))
                    )}
                </div>

                </div>

                <Divider orientation="vertical" flexItem sx={{backgroundColor:"rgb(89,54,45)"}} /> 
                
                <div className = "user-profile">
                    <div className="profile-pic">
                    <input id = "portrait-upload" type ="file" accept="image/*"/>
                    <label htmlFor="portrait-upload">
                        <AccountCircleIcon sx={{
                                fontSize:100,
                                borderRadius:'5px',
                        }} />
                    </label>
                    </div>
                    <div className="profile-content">
                    <p>Email: <input type ="text" value="jessica12@gmail.com" disabled /></p>
                    <p>Change Password: <input type= "text"/></p>
                    </div>

                </div>

            </div>
    );
}

export default Profile;