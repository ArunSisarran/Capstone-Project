import React from 'react'
import {useState} from 'react'
import PersonIcon from '@mui/icons-material/Person';
import EmailIcon from '@mui/icons-material/Email';
import LockIcon from '@mui/icons-material/Lock';
import {Link, useNavigate} from 'react-router-dom'
import '../pages/Login-SignupForm.css'

function Signup(){
    const [form, setForm] = useState({
        username:"",
        email:"",
        password:"",
    });

    const handleFormChange = (e) =>{
        setForm({...form, [e.target.name]:e.target.value});
    }

    const navigate = useNavigate();

    const handleSubmit = (e) =>{
        e.preventDefault();
        
    }


    return(
        <>
        <div className="page">
            <div className="container">

                <h1>Sign Up</h1>

                <form action ="">

                    <div className="inputs">
                        <input 
                            type = "text" 
                            placeholder="Username" 
                            value = {form.username}
                            onChange={handleFormChange}
                            required
                        />
                        <PersonIcon className="icons" />
                    </div>

                    <div className="inputs">
                        <input 
                            type = "email" 
                            placeholder="Email Address"
                            value = {form.email}
                            onChange={handleFormChange}
                            required
                        />
                        <EmailIcon className="icons" />
                    </div>

                    <div className="inputs">
                        <input 
                            type = "password" 
                            placeholder="Password"
                            value = {form.password}
                            onChange={handleFormChange}                           
                            required
                        />
                        <LockIcon className="icons" />
                    </div>


                    <div className="submit-container">
                        <button className="submit">Sign Up</button>
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