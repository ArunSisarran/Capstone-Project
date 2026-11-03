import React from 'react'
import {useState} from 'react'
import PersonIcon from '@mui/icons-material/Person';
import EmailIcon from '@mui/icons-material/Email';
import LockIcon from '@mui/icons-material/Lock';
import {Link, useNavigate} from 'react-router-dom'
import '../css/Login-SignupForm.css'
import {useForm, Form} from 'react-hook-form'

function Signup(){
    const {register, handleSubmit,formState: {errors},}
     = useForm()

    const onSubmit = async(registerData) => {
        const response = await fetch (
            "http://127.0.0.1:8000/auth/signup",
            {
            method : "POST",
            headers:{
                "Content-Type":"application/json",
            },
            body: JSON.stringify(registerData),
        });

    const data = await response.json();

    console.log("Status:", response.status);
    console.log(data);
    };

    return(
        <>
        <div className="page">
            <div className="container">

                <h1>Sign Up</h1>

                <form 
                    onSubmit={handleSubmit(onSubmit)}
                >

                    <div className="inputs">
                        <input 
                            type = "email" 
                            placeholder="you@example.com"
                            {...register("email",{
                            required:"Email is required",
                            pattern:{value:/^\S+@\S+\.\S+$/, message:"Invalid email!Please re-enter!"},
                            })}
                        />
                        <EmailIcon className="icons" />

                        <p>{errors.email?.message}</p>
                    </div>

                    <div className="inputs">
                        <input 
                            type = "password" 
                            placeholder="Password"                          
                            {...register("password",{
                                required:"Password is required",
                                minLength:{value: 8, message:"Must be 8 characters"},
                                pattern:{message:"Invalid password. Please re-enter"},
                            })}
                        />
                        <LockIcon className="icons" />
                        <p>{errors.password?.message}</p>
                    </div>   


                    <div className="submit-container">
                        <button type ="submit" className="submit">Sign Up</button>
                    </div>

                    <div className="login-register">
                        <p>Have account already? {""}
                            <Link to="/login">Login</Link>
                        </p>
                    </div>

                </form>
            </div>
        </div>
        </>
    );
} 

export default Signup;