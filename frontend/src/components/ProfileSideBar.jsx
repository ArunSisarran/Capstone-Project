import React,{useState,useEffect} from 'react'
import '../css/Profile.css'
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import {useNavigate} from 'react-router-dom';
import Divider from '@mui/material/Divider';
import {useAuth} from '../context/AuthContext'


function ProfileSideBar(){
    const navigate = useNavigate();

    const {user, isLoggedIn,loading} = useAuth();


     if (loading) return <p>Loading...</p>;

    //navigate to other pages
    const handleHistoryPage = () => {
        navigate("/profile")
    };

    const handleFavoritePage = () =>{
        navigate("/favorite")
    };

    const handleSavedForLaterPage = () =>{
        navigate("/savedforlater")
    };
    

    const handleChangePassword = () =>{
        navigate("/changepassword")
    }



    return (
        <>

            <div className = "user-profile">
                <div className="profile-pic">
                
                <input 
                    id = "portrait-upload" 
                    type ="file" 
                    accept="image/*"
                />

                <label htmlFor="portrait-upload">
                    <AccountCircleIcon sx={{
                            fontSize:100,
                            borderRadius:'5px',
                    }} />
                </label>

               
                    <div className="profile-content">
                    
                        {
                            isLoggedIn ? (
                                <h3>{user?.email}</h3>
                            ):(
                                <h3>Please Login</h3>
                            )
                        }
                    
                        
                        <span className="change-password">
                        <button onClick = {handleChangePassword}>Change Password</button>
                        </span>
                    </div>

                 </div>

                <Divider flexItem sx={{backgroundColor:"rgb(89,54,45)"}} /> 

                <span className = "buttons">
                <button onClick = {handleHistoryPage}> History </button>
                <button onClick = {handleFavoritePage}> Favorites </button>
                <button onClick = {handleSavedForLaterPage}>Saved For Later </button>
                </span>
                
            </div>
        </>
    )
}

export default ProfileSideBar;