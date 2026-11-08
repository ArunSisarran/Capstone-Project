import React,  {useState} from 'react'
import PersonIcon from '@mui/icons-material/Person';
import EmailIcon from '@mui/icons-material/Email';
import LockIcon from '@mui/icons-material/Lock';
import '../css/Login-SignupForm.css'
import '../components/Navbar'
import {Link,useNavigate} from 'react-router-dom'
import {useForm} from 'react-hook-form'

function ChangePassword({token,setToken}){

    const {register, handleSubmit,formState:reset,setError}
     = useForm();


    //calling api from frontend for login
    const onSubmit = async(passwordData) => {


        const response = await fetch (
            "http://127.0.0.1:8000/users/me/password",
            {
            method : "PUT",
            headers:{
                "Content-Type":"application/json",
                Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify(passwordData),
        });  

        const data = await response.json();

        if(!response.ok){
            throw new Error("Failed to change password");
        }

        reset();

    
    };



    return(
    <div className="page">
        <div className="container">

            <h1>Change Password</h1>

            <form onSubmit={handleSubmit(onSubmit)}>

                <div className="inputs">
                    <input 
                        type = "password" 
                        placeholder="Enter Current Password"
                        {...register("currentPassword",{
                        required:"Current Password is required",
                        })}
                    />
                    <EmailIcon className="icons" />
                    <p>{errors.email?.message}</p>
                </div>

                <div className="inputs">
                    <input 
                        type = "password" 
                        placeholder="Enter New Password"                          
                        {...register("password",{
                            required:"Password is required",
                            minLength:{value: 8, message:"Must be 8 characters"},
                            pattern:{message:"Invalid password.Please re-enter!"},
                        })}
                    />
                    <LockIcon className="icons" />
                    <p>{errors.password?.message}</p>
                </div>


                <div className="submit-container">
                    <button type="submit">Update Password</button>
                </div>

            </form>

        </div>
    </div>
    );
} 

export default ChangePassword;