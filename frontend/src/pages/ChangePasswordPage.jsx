import React,  {useState} from 'react'
import PersonIcon from '@mui/icons-material/Person';
import EmailIcon from '@mui/icons-material/Email';
import LockIcon from '@mui/icons-material/Lock';
import '../css/Login-SignupForm.css'
import '../components/Navbar'
import {Link,useNavigate} from 'react-router-dom'
import {useForm} from 'react-hook-form'
import {base_url} from '../api/api.js'

function ChangePassword(){

    const {register, handleSubmit,reset,formState:{errors}}
     = useForm();

    
    const [success, setSuccess] = useState(false);
    const [error, setError] = useState("");

    //calling api from frontend for login
    const onSubmit = async(passwordData) => {

    console.log("Form Data:",passwordData);

    const savedToken = localStorage.getItem("token")

    try{

        const response = await fetch (
            `${base_url}/users/me/password`,
            {
            method : "PUT",
            headers:{
                "Content-Type":"application/json",
                Authorization: `Bearer ${savedToken}`,
            },
            body: JSON.stringify(passwordData),
        });  

        const data = await response.json();

        console.log("Status:", response.status);
        console.log("Backend Error:", data);

        if(!response.ok){
            throw new Error("Failed to change password");
        }

      reset();
      setSuccess(true);

    } catch (error){
         setError(error.message);
    }

    
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
                    <p>{errors.password?.message}</p>
                </div>

                <div className="inputs">
                    <input 
                        type = "password" 
                        placeholder="Enter New Password"                          
                        {...register("newPassword",{
                            required:"Password is required",
                            minLength:{value: 8, message:"Must be 8 characters"},
                            pattern:{message:"Invalid password.Please re-enter!"},
                        })}
                    />
                    <LockIcon className="icons" />
                    <p>{errors.password?.message}</p>
                </div>


                {success && (
                    <p style={{color:"green"}}> Login successful!</p>
                )}

                <div className="submit-container">
                    <button type="submit">Update Password</button>
                </div>

            </form>

        </div>
    </div>
    );
} 

export default ChangePassword;