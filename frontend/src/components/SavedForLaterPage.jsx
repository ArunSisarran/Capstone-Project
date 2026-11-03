import React, {useState, useEffect} from 'react'
import '../css/Profile.css'
import Divider from '@mui/material/Divider';
import { Link} from 'react-router-dom'
import FavoriteButton from '../components/FavoriteButton'
import SavedForLaterButton from '../components/SavedForLaterButton'
import ProfileSideBar from '../components/ProfileSideBar'

function SavedForLaterPage({favorites,setFavorites,savedforlater,setSavedForLater,token,setToken}){

     useEffect(() =>{
    const later = JSON.parse(localStorage.getItem("clickSaved")) || [];
     setSavedForLater(later);
    },[]);

    return(
        <div className = "profile-page">
            <div className = "track-list">
            <div className="SavedForLater">
                    <h1>Saved For Later </h1>
                    <Divider sx={{backgroundColor:"rgb(89,54,45)"}} />
                    {savedforlater.length === 0 ?(
                        <p>Empty History</p>
                    ):(
                    savedforlater.map((recipe)=>(
                        <div className ="history-info" key={recipe.id}>
                            <span className="time-title">
                            <p>{new Date(recipe.viewedAt).toLocaleDateString("en-US")}</p>
                            <Link to={`/result/${recipe.id}`} className="link">{recipe.title} </Link>
                            </span>
                            <span className="info-buttons">
                            <FavoriteButton recipe={recipe} favorites={favorites} setFavorites={setFavorites}/>
                            <SavedForLaterButton recipe={recipe} savedforlater={savedforlater} setSavedForLater={setSavedForLater} />
                            </span>
                        </div>
                        ))
                    )}
                </div>
                    <Divider orientation="vertical" flexItem sx={{backgroundColor:"rgb(89,54,45)"}} /> 
                    <ProfileSideBar token={token} setToken={setToken}/>
                    </div>
                </div>
    )
}

export default SavedForLaterPage;