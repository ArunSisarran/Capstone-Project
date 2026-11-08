import React,  {useState} from 'react'
import PersonIcon from '@mui/icons-material/Person';
import EmailIcon from '@mui/icons-material/Email';
import LockIcon from '@mui/icons-material/Lock';
import '../css/Login-SignupForm.css'
import '../components/Navbar'
import {Link,useNavigate} from 'react-router-dom'
import {useForm} from 'react-hook-form'
import {base_url} from '../api/api.js'
import {useAuth} from '../context/AuthContext'

function Login({token,setToken}){

    const {register, handleSubmit,formState: {errors},}
     = useForm()

    const {login} = useAuth();

    //calling api from frontend for login
    const onSubmit = async(loginData) => {
        const response = await fetch (
            `${base_url}/auth/login`,
            {
            method : "POST",
            headers:{
                "Content-Type":"application/json",
            },
            body: JSON.stringify(loginData),
        });

        const data = await response.json();

        if(!response.ok){
            throw new Error("Login failed!");
            
        }

        login(data.user,data.access_token)
    };



    return(
    <div className="page">
        <div className="container">

            <h1>Login</h1>

            <form onSubmit={handleSubmit(onSubmit)}>

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
                            pattern:{message:"Invalid password.Please re-enter!"},
                        })}
                    />
                    <LockIcon className="icons" />
                    <p>{errors.password?.message}</p>
                </div>

                <div className="submit-container">
                    <button type="submit">Login</button>
                </div>

                <div className="login-register">
                    <p>Don't have an account? {""}
                        <Link to="/signup">Sign Up</Link>
                    </p>
                    <br></br>
                    <a href="#"> Forget Password </a>
                </div>

            </form>

        </div>
    </div>
    );
} 

export default Login;