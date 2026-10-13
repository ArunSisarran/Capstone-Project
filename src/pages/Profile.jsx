import React from 'react'
import {useEffect, useState} from 'react'
import '../pages/Profile.css'
import Divider from '@mui/material/Divider';

function Profile(){



    return(
        <div className = "profile-page">
            <div className="track-list">
                <div className="history">
                        <h1>Recent History </h1>
                        <Divider sx={{backgroundColor:"rgb(89,54,45)"}} />

                        <ul >
                            <li>Recipe1</li>
                            <li>Recipe2</li>                    
                        </ul>
                    </div>

                    <div className="favorites">
                        <h1>Favorite Recipes</h1>
                        <Divider sx={{backgroundColor:"rgb(89,54,45)"}} />
                        <ul>
                            <li>Recipe1</li>
                            <li>Recipe2</li>                    
                        </ul>
                    </div>

                    <div className="SavedForLater">
                        <h1>Saved For Later </h1>
                        <Divider sx={{backgroundColor:"rgb(89,54,45)"}} />
                        <ul>
                            <li>Recipe1</li>
                            <li>Recipe2</li>                    
                        </ul>
                    </div>

                </div>

                <div className = "user-profile">

                <div className="profile-pic">

                </div>
                <p>Username: <input type ="text" value="Jessica" disabled /></p>
                <p>Email: <input type ="text" value="jessica12@gmail.com" disabled /></p>
                </div>

            </div>
    );
}

export default Profile;