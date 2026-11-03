import React,{useState,useEffect} from 'react'
import '../css/Profile.css'
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import {useNavigate} from 'react-router-dom';
import Divider from '@mui/material/Divider';


function ProfileSideBar({token,setToken}){
    const navigate = useNavigate();

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

    const [user,setUser] = useState([]);
       
    //calling api for get user email address
    useEffect (()=>{
        const getUser = async () =>{
            const response = await fetch("http://127.0.0.1:8000/users/me",{
                headers:{
                    Authorization: `Bearer ${token}`
                }
            });
            if(!response.ok){
                throw new Error("Failed!")
            }
            const data = await response.json();
            setUser(data);
        };

        getUser();
    },[]);



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
                        <h3>Email:{user.email}</h3>
                        <span className="change-password">
                        <button>Change Password</button>
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